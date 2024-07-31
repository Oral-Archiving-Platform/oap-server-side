from django.db import models
from apps.media.models import Media, Category
from apps.users.models import User

class Ebook(Media):
    file = models.FileField(upload_to='ebooks/')
    drm_protected = models.BooleanField(default=True)

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

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if self.type != 'true_false':
            self.correct_answer = None
        super().save(*args, **kwargs)


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
