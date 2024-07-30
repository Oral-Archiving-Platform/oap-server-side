from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EbookViewSet, QuizViewSet, QuestionViewSet, QuizSubmissionViewSet, OptionViewSet
from apps.media.views import CategoryViewSet  # Correctly import from media

router = DefaultRouter()
router.register(r'ebooks', EbookViewSet, basename='ebook')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'submissions', QuizSubmissionViewSet, basename='submission')
router.register(r'options', OptionViewSet, basename='options')

urlpatterns = router.urls