from rest_framework import serializers
from .models import Ebook, Quiz, Question, QuizSubmission
from apps.media.models import Category, Media

class EbookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.name', read_only=True)

    class Meta:
        model = Ebook
        exclude = ['uploaderID']
    


class QuestionSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question_text', 'type', 'correct_answer', 'options', 'correct_option']

    

    def validate(self, data):
        if data['type'] == 'multiple_choice' and data.get('correct_answer'):
            raise serializers.ValidationError("Multiple choice questions should not have a correct_answer directly.")


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'ebook', 'questions']