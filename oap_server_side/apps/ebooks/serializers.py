from rest_framework import serializers
from .models import Ebook, Quiz, Question, QuizSubmission
from apps.media.models import Category, Media
from apps.media.serializers import CommentSerializer

class EbookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.name', read_only=True)
    uploader_name = serializers.CharField(source='uploaderID.username', read_only=True) 
    class Meta:
        model = Ebook
        exclude = ['uploaderID']


class EbookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ebook
        fields = ['id', 'title', 'description']

class EbookInfoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.name', read_only=True)
    thumbnail_url = serializers.ImageField(source='thumbnail', read_only=True)  # URL for the thumbnail image

    class Meta:
        model = Ebook
        fields = ['thumbnail_url', 'title', 'description', 'category_name']

class QuestionSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question_text', 'type', 'correct_answer', 'options', 'correct_option']

    def validate(self, data):
        if data['type'] == 'multiple_choice':
            if data.get('correct_answer'):
                raise serializers.ValidationError("Multiple choice questions should not have a correct_answer directly.")
            if not data.get('options'):
                raise serializers.ValidationError("Multiple choice questions must have options.")
            if not data.get('correct_option'):
                raise serializers.ValidationError("Multiple choice questions must have a correct option.")
            if data['correct_option'] not in data['options']:
                raise serializers.ValidationError("The correct option must be one of the provided options.")
        elif data['type'] == 'true_false':
            if data.get('options'):
                raise serializers.ValidationError("True/False questions should not have options.")
            if not data.get('correct_answer'):
                raise serializers.ValidationError("True/False questions must have a correct answer.")
            if data['correct_answer'] not in ['True', 'False']:
                raise serializers.ValidationError("The correct answer for a True/False question must be 'True' or 'False'.")
            if data.get('correct_option'):
                raise serializers.ValidationError("True/False questions should not have a correct_option.")

        # Always return the validated data
        return data

class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'ebook', 'questions']