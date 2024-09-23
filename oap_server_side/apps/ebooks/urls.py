from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EbookViewSet, 
    QuizViewSet, 
    QuestionViewSet, 
    QuizSubmissionViewSet, 
    EbookInfoView, 
    EbookSearchView,
    ReadLaterViewSet
)

router = DefaultRouter()
router.register(r'ebooks', EbookViewSet, basename='ebook')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'submissions', QuizSubmissionViewSet, basename='submission')
router.register(r'read-later', ReadLaterViewSet, basename='read-later')

urlpatterns = [
    path('ebooks/search/', EbookSearchView.as_view(), name='ebook-search'),
    path('', include(router.urls)),
    path('ebooks/<int:pk>/info/', EbookInfoView.as_view(), name='ebook-info'),  # Update
    path('ebooks/<int:pk>/comments/', EbookViewSet.as_view({'get': 'comments', 'post': 'comments'}), name='ebook-comments'),

]
