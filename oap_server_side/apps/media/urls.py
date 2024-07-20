from .views import CategoryViewSet, MediaViewSet, CommentViewSet, ViewViewSet,UserActivityViewSet
from rest_framework.routers import DefaultRouter, path
from django.urls import path, include

router = DefaultRouter()
router.register(r'media', MediaViewSet, basename='medias')
router.register(r'category', CategoryViewSet,basename='categories')
router.register(r'comment', CommentViewSet,basename='comments')
router.register(r'view', ViewViewSet,basename='views')
router.register(r'user-activity', UserActivityViewSet, basename='user-activity')


urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),
]