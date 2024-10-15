from .views import ChannelViewSet, ChannelMembershipViewSet, SubscriptionViewSet, UserChannelViewSet, ChanneVideolViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'channel_membership', ChannelMembershipViewSet,basename='channel_membership')
router.register(r'subscription', SubscriptionViewSet,basename='subscription')

router.register(r'user_channel', UserChannelViewSet,basename='user_channel')
router.register(r'channel_videos', ChanneVideolViewSet, basename='channel-videos')

urlpatterns = router.urls