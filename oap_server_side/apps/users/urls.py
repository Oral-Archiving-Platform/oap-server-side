from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MyTokenObtainPairView, generate_qr_code, UserRegister, VerifyTokenView, TestView, UserViewSet, verify_2fa

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', VerifyTokenView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('generate-qr/', generate_qr_code, name='generate_qr'),
    path('verify-2fa/', verify_2fa, name='verify_2fa'),
]
