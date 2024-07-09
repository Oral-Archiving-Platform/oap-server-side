from .views import CategoryViewSet, MediaViewSet, CommentViewSet, ViewViewSet, LikeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'media', MediaViewSet, basename='medias')
router.register(r'category', CategoryViewSet,basename='categories')
router.register(r'comment', CommentViewSet,basename='comments')
router.register(r'view', ViewViewSet,basename='views')
router.register(r'like', LikeViewSet,basename='likes')


urlpatterns = router.urls