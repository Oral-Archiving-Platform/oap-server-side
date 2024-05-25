from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from oap_server_side.users import admin
from .views import UserRegister, VerifyTokenView, TestView, UserRoleView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', VerifyTokenView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('role/', UserRoleView.as_view(), name='role'),
]
