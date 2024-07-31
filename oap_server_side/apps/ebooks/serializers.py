from rest_framework import serializers
from .models import Ebook, Quiz, Question, Option, QuizSubmission
from apps.media.models import Category, Media

class EbookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.name', read_only=True)

    class Meta:
        model = Ebook
        fields = '__all__'


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'
class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question_text', 'type', 'correct_answer','options']

    def validate(self, data):
        if data['type'] == 'true_false':
            if data.get('correct_answer') not in ['True', 'False']:
                raise serializers.ValidationError("Invalid correct answer for True/False question.")
        elif data['type'] == 'multiple_choice':
            if 'correct_answer' in data:
                data.pop('correct_answer')  # Ensure it's removed if somehow passed
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