from django.contrib import admin
from .models import Ebook, Quiz, Question, Option, QuizSubmission

admin.site.register(Ebook)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizSubmission)
