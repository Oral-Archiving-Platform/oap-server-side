from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, UserInfoSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from rest_framework.generics import ListAPIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import qrcode
import base64
import os
from django.conf import settings
import pyotp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if this.action == 'list' or this.action == 'retrieve':
            return UserInfoSerializer
        return UserSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Ensure proper permissions

class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'valid': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if not token:
            return Response({'error': 'Authorization token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = token.split(' ')[1]
            decoded_token = AccessToken(token)
            user_role = decoded_token.get('role', 'No role assigned')
            return Response({'role': user_role}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'error': 'Invalid token or token has expired', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except IndexError:
            return Response({'error': 'Invalid token format'}, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['id'] = user.id
        token['role'] = user.role
        # token['picture'] = user.picture.url if user.picture else None  # Remove or comment out this line

        totp_device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
        if created:
            totp_device.save()
            logger.info(f"TOTP device created during login for user: {user.username}")
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        logger.info(f"Attempting login for user: {username} with password: {password}")
        print(f"Attempting login for user: {username} with password: {password}")

        response = super().post(request, *args, **kwargs)
        
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            logger.info(f"User {username} logged in successfully.")
            print(f"User {username} logged in successfully.")
        else:
            logger.error(f"Failed to authenticate user: {username}")
            print(f"Failed to authenticate user: {username}")

        return response

class UserRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User Created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestView(APIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)

@login_required
def generate_qr_code(request):
    user = request.user
    logger.debug(f"User for QR Code generation: {user.username}")
    print(f"User for QR Code generation: {user.username}")
    
    totp_device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
    if created:
        totp_device.save()
        logger.info(f"TOTP device created for user: {user.username}")
        print(f"TOTP device created for user: {user.username}")

    secret = base64.b32encode(totp_device.bin_key).decode('utf-8')
    logger.debug(f"Encoded Secret: {secret}")
    print(f"Encoded Secret: {secret}")

    totp_url = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="YourApp")
    logger.debug(f"TOTP Device Config URL: {totp_url}")
    print(f"TOTP Device Config URL: {totp_url}")

    qr = qrcode.make(totp_url)

    static_dir = os.path.join(settings.BASE_DIR, 'static')
    logger.debug(f"Static directory path: {static_dir}")
    print(f"Static directory path: {static_dir}")
    if not os.path.exists(static_dir):
        logger.info("Static directory does not exist. Creating...")
        print("Static directory does not exist. Creating...")
        os.makedirs(static_dir)
    else:
        logger.info("Static directory exists.")
        print("Static directory exists.")

    qr_code_path = os.path.join(static_dir, 'qr_code.png')
    logger.debug(f"QR code path: {qr_code_path}")
    print(f"QR code path: {qr_code_path}")

    try:
        qr.save(qr_code_path)
        logger.info(f"QR code saved at: {qr_code_path}")
        print(f"QR code saved at: {qr_code_path}")
    except Exception as e:
        logger.error(f"Error saving QR code: {e}")
        print(f"Error saving QR code: {e}")
        return JsonResponse({'error': 'Could not save QR code'}, status=500)

    return JsonResponse({'qr_url': 'static/qr_code.png'})

@login_required
def verify_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        user = request.user
        logger.debug(f"Username for 2FA: {user.username}")
        print(f"Username for 2FA: {user.username}")
        
        try:
            totp_device = TOTPDevice.objects.get(user=user, name='default')
            secret = base64.b32encode(totp_device.bin_key).decode('utf-8')
            logger.debug(f"Token received: {token}")
            logger.debug(f"Shared Secret: {secret}")
            logger.debug(f"Config URL: {totp_device.config_url}")
            logger.debug(f"Current server time: {datetime.now()}")
            print(f"Token received: {token}")
            print(f"Shared Secret: {secret}")
            print(f"Config URL: {totp_device.config_url}")
            print(f"Current server time: {datetime.now()}")

            totp = pyotp.TOTP(secret)
            current_valid_token = totp.now()
            pyotp_verified = totp.verify(token, valid_window=1)
            logger.debug(f"pyotp verification result: {pyotp_verified}")
            print(f"pyotp verification result: {pyotp_verified}")
            print(f"Expected token: {current_valid_token}")

            if pyotp_verified:
                request.session['otp_verified'] = True
                logger.info(f"User {user.username} 2FA verified successfully.")
                print(f"User {user.username} 2FA verified successfully.")
                return JsonResponse({'message': '2FA verified successfully'})
            else:
                logger.warning(f"Invalid token for user {user.username}. Expected token: {current_valid_token}")
                print(f"Invalid token for user {user.username}. Expected token: {current_valid_token}")
                return JsonResponse({'error': 'Invalid token'}, status=400)
        except TOTPDevice.DoesNotExist:
            logger.error(f"TOTP device not found for the user: {user.username}")
            print(f"TOTP device not found for the user: {user.username}")
            return JsonResponse({'error': 'TOTP device not found for the user'}, status=400)
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            print(f"Exception: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'verify_2fa.html')
