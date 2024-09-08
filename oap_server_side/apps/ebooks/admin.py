from django.contrib import admin
from .models import Ebook, Quiz, Question, QuizSubmission

admin.site.register(Ebook)
admin.site.register(Quiz)
admin.site.register(Question)

admin.site.register(QuizSubmission)
