from .views import ChannelViewSet, ChannelMembershipViewSet, SubscriptionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'channel_membership', ChannelMembershipViewSet,basename='channel_membership')
router.register(r'subscription', SubscriptionViewSet,basename='subscription')


urlpatterns = router.urls