from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Ebook, Quiz, Question, Option, QuizSubmission
from .serializers import EbookSerializer, QuizSerializer, QuestionSerializer, OptionSerializer, QuizSubmissionSerializer

class EbookViewSet(viewsets.ModelViewSet):
    queryset = Ebook.objects.all()
    serializer_class = EbookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        # Custom logic to grade the quiz and store the submission
        # Example implementation
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
                    is_correct = question.options.filter(text=selected_option, is_correct=True).exists()
                    if is_correct:
                        total_score += 1
            elif question.type == 'multiple_choice':
                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and correct_option.text == selected_option:
                    total_score += 1

        QuizSubmission.objects.create(user=user, quiz=quiz, score=total_score)

        return Response({"message": "Quiz submitted successfully.", "score": total_score})
