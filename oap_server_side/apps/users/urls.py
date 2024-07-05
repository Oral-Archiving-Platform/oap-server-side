from django.urls import path
from .views import MyTokenObtainPairView, generate_qr_code, UserRegister, VerifyTokenView, TestView, UserRoleView,verify_2fa
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('verify/', VerifyTokenView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('role/', UserRoleView.as_view(), name='role'),
    path('generate-qr/', generate_qr_code, name='generate_qr'),
    path('verify-2fa/', verify_2fa, name='verify_2fa'),
]
