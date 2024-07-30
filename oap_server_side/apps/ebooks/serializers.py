from rest_framework import serializers
from .models import Ebook, Quiz, Question, Option, QuizSubmission
from apps.media.models import Category, Media

class EbookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='categoryID.name', read_only=True)

    class Meta:
        model = Ebook
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = '__all__'
