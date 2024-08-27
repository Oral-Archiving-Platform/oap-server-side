from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Ebook, Quiz, Question, QuizSubmission
from .serializers import EbookSerializer, QuizSerializer, QuestionSerializer, QuizSubmissionSerializer
from random import sample
from rest_framework import generics, permissions
from apps.ebooks.serializers import EbookInfoSerializer
from django.db.models import Q
from .models import Ebook
from .serializers import EbookSearchSerializer
from django.contrib.postgres.search import TrigramSimilarity

class EbookInfoView(generics.RetrieveAPIView):  # Change from ListAPIView to RetrieveAPIView
    queryset = Ebook.objects.all()
    serializer_class = EbookInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class EbookSearchView(generics.ListAPIView):
    serializer_class = EbookSearchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query = self.request.query_params.get('title', '')
        if not query:
            return Ebook.objects.none()
        return Ebook.objects.filter(title__icontains=query)


class EbookViewSet(viewsets.ModelViewSet):
    queryset = Ebook.objects.all()
    serializer_class = EbookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(uploaderID=self.request.user)
    
from rest_framework.decorators import action

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'], url_path='submit', url_name='submit')
    def submit(self, request, pk=None):
        user = request.user
        data = request.data
        quiz_id = pk
        user_answers = data.get('answers', [])
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        total_score = 0
        feedback = []
        total_questions_answered = len(user_answers)

        for answer in user_answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('selected_option')
            
            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
            except Question.DoesNotExist:
                continue

            correct = False
            correct_answer = None

            if question.type == 'true_false':
                correct_answer = question.correct_answer
                correct = selected_option.lower() == correct_answer.lower()
                if correct:
                    total_score += 1
            elif question.type == 'multiple_choice':
                correct_option = question.correct_option
                correct = correct_option == selected_option
                if correct:
                    total_score += 1

            feedback.append({
                "question_id": question.id,
                "question_text": question.question_text,
                "selected_option": selected_option,
                "correct_answer": correct_answer if question.type == 'true_false' else correct_option,
                "correct": correct,
            })

        # Calculate the percentage score
        if total_questions_answered > 0:
            percentage_score = (total_score / total_questions_answered) * 100
        else:
            percentage_score = 0  # Handle edge case where no questions were answered

        QuizSubmission.objects.create(user=user, quiz=quiz, score=percentage_score)
        return Response({
            "message": "Quiz is submitted successfully.",
            "score": percentage_score,
            "feedback": feedback
        }, status=status.HTTP_201_CREATED)

   
    @action(detail=False, methods=['post'], url_path='generate', url_name='generate_quiz')
    def generate_quiz(self, request):
        ebook_id = request.data.get('ebook_id')
        
        if not ebook_id:
            return Response({"error": "Ebook ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ebook = Ebook.objects.get(id=ebook_id)
        except Ebook.DoesNotExist:
            return Response({"error": "Ebook not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all related questions for the ebook
        related_questions = Question.objects.filter(quiz__ebook=ebook)

        if len(related_questions) < 10:
            return Response({"error": "Not enough questions to generate a quiz."}, status=status.HTTP_400_BAD_REQUEST)

        # Separate multiple choice and true/false questions
        multiple_choice_questions = [q for q in related_questions if q.type == 'multiple_choice']
        true_false_questions = [q for q in related_questions if q.type == 'true_false']

        if len(multiple_choice_questions) < 4 or len(true_false_questions) < 6:
            return Response({"error": "Not enough questions to meet the required ratio."}, status=status.HTTP_400_BAD_REQUEST)

        # Randomly select questions based on the ratio
        selected_mc_questions = sample(multiple_choice_questions, 4)  # 40% of 10 is 4
        selected_tf_questions = sample(true_false_questions, 6)  # 60% of 10 is 6

        # Combine the selected questions
        selected_questions = selected_mc_questions + selected_tf_questions

        # Create a new quiz
        new_quiz = Quiz.objects.create(
            ebook=ebook,
            title=f"Generated Quiz for {ebook.title}"
        )

        # Add selected questions to the new quiz
        for question in selected_questions:
            question.quiz = new_quiz
            question.save()

        return Response({
            "message": "Quiz generated successfully.",
            "quiz_id": new_quiz.id,
            "questions": QuestionSerializer(selected_questions, many=True).data
        }, status=status.HTTP_201_CREATED)
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data
        question_type = data.get('type')
        options = data.get('options', [])
        correct_option = data.get('correct_option')

        if question_type == 'multiple_choice':
            if not options or correct_option not in options:
                return Response({"error": "Options must include the correct option."}, status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.create(
                quiz_id=data.get('quiz'),
                question_text=data.get('question_text'),
                type=question_type,
                options=options,
                correct_option=correct_option,  
                correct_answer=None  # Correct answer is not used for multiple choice
            )

        elif question_type == 'true_false':
            correct_answer = data.get('correct_answer')
            if correct_answer not in ['True', 'False']:
                return Response({"error": "Invalid or missing correct_answer for True/False question."}, status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.create(
                quiz_id=data.get('quiz'),
                question_text=data.get('question_text'),
                type=question_type,
                options=None,  # No options for true/false questions
                correct_answer=correct_answer
            )

        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        quiz_id = data.get('quiz_id')
        user_answers = data.get('answers', [])
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        total_score = 0
        for answer in user_answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('selected_option')
            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
            except Question.DoesNotExist:
                continue

            if question.type == 'true_false':
                if selected_option.lower() in ['true', 'false']:
                    is_correct = (question.correct_answer and selected_option.lower() == 'true') or \
                                 (not question.correct_answer and selected_option.lower() == 'false')
                    if is_correct:
                        total_score += 1
            elif question.type == 'multiple_choice':
                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and correct_option.text == selected_option:
                    total_score += 1

        QuizSubmission.objects.create(user=user, quiz=quiz, score=total_score)
        return Response({"message": "Quiz submitted successfully.", "score": total_score}, status=status.HTTP_201_CREATED)