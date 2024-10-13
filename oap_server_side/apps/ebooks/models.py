from django.db import models
from apps.media.models import Media, Category
from apps.users.models import User

class Ebook(Media):
    file = models.FileField(upload_to='ebooks/')
    drm_protected = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)  # New field for the thumbnail
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE,related_name='ebook_media')

    def __str__(self):
        return self.title

class Quiz(models.Model):
    ebook = models.ForeignKey(Ebook, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    QUESTION_TYPES = [
        ('true_false', 'True/False'),
        ('multiple_choice', 'Multiple Choice'),
    ]
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    correct_answer = models.CharField(max_length=20, choices=[('True', 'True'), ('False', 'False')], null=True, blank=True)
    options = models.JSONField(null=True, blank=True)  # JSON field to store options
    correct_option = models.CharField(max_length=255, null=True, blank=True)  # New field to store the correct option

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if self.type == 'multiple_choice':
            self.correct_answer = None  # Correct answer is not needed for multiple choice
        super().save(*args, **kwargs)

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"