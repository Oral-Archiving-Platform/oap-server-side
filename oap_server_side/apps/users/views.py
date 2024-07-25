# views.py
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from rest_framework.decorators import api_view, permission_classes, action
from django.http import JsonResponse
import qrcode
import base64
import os
from django.conf import settings
import pyotp
from datetime import datetime
import logging
from django.http import FileResponse, HttpResponse
import io

from .serializers import UserSerializer, UserInfoSerializer, MyTokenObtainPairSerializer
from .models import User
from ..users.permissions import IsAdmin

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserInfoSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_role(self, request):
        """
        Returns the user role based on the provided authorization token.
        """
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

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        logger.info(f"Attempting login for user: {username}")

        response = super().post(request, *args, **kwargs)

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            access = response.data.get('access')

            if not user.is_2fa_completed:
                request.session['2fa_user_id'] = user.id
                logger.info(f"User {username} requires 2FA verification.")

                # Automatically generate QR code for 2FA
                totp_device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
                if created:
                    totp_device.save()
                    logger.info(f"TOTP device created for user: {user.username}")

                secret = base64.b32encode(totp_device.bin_key).decode('utf-8')
                totp_url = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="YourApp")
                qr = qrcode.make(totp_url)
                qr_code_buffer = io.BytesIO()
                qr.save(qr_code_buffer, format='PNG')
                qr_code_buffer.seek(0)

                qr_code_filename = f'qr_code_{user.username}.png'
                qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_code_filename)
                qr_code_url = os.path.join(settings.MEDIA_URL, 'qr_codes', qr_code_filename)

                os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)
                with open(qr_code_path, 'wb') as f:
                    f.write(qr_code_buffer.read())

                logger.info(f"QR code saved at: {qr_code_path}")

                # Return the URL of the QR code image along with 2FA required message
                return JsonResponse({
                    'message': '2FA required',
                    'qr_code_url': qr_code_url,
                    'token': access
                }, status=status.HTTP_200_OK)

            else:
                logger.info(f"User {username} logged in successfully.")
                return response
        else:
            logger.error(f"Failed to authenticate user: {username}")
            return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

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
        token['is_2fa_completed'] = user.is_2fa_completed  # Add is_2fa_completed to token

        totp_device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
        if created:
            totp_device.save()
            logger.info(f"TOTP device created during login for user: {user.username}")
        return token
    
from rest_framework.permissions import IsAuthenticated

class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        user = request.user
        return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)

    

class VerifyTokenView2FA(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        logger.info(f"Attempting login for user: {username}")

        # Authenticate the user with username and password
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                # Check if the user has completed 2FA
                if not user.is_2fa_completed:
                    logger.info(f"User {username} requires 2FA verification.")
                    try:
                        # Retrieve the TOTP device for the user
                        totp_device = TOTPDevice.objects.get(user=user, name='default')
                        if totp_device:
                            request.session['2fa_user_id'] = user.id
                            return JsonResponse({'message': '2FA required'}, status=status.HTTP_401_UNAUTHORIZED)
                    except TOTPDevice.DoesNotExist:
                        logger.error(f"TOTP device not found for user: {user.username}")
                        return JsonResponse({'error': '2FA setup incomplete'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    logger.info(f"User {username} logged in successfully.")
                    return JsonResponse({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'Account disabled'}, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.error(f"Failed to authenticate user: {username}")
            return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_qr_code(request):
    user = request.user
    logger.debug(f"User for QR Code generation: {user.username}")

    # Retrieve or create TOTP device for the user
    totp_device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
    if created:
        totp_device.save()
        logger.info(f"TOTP device created for user: {user.username}")

    # Generate TOTP secret and URL
    secret = base64.b32encode(totp_device.bin_key).decode('utf-8')
    logger.debug(f"Encoded Secret: {secret}")

    totp_url = pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="YourApp")
    logger.debug(f"TOTP Device Config URL: {totp_url}")

    # Generate QR code image
    qr = qrcode.make(totp_url)
    qr_code_buffer = io.BytesIO()
    qr.save(qr_code_buffer, format='PNG')
    qr_code_buffer.seek(0)

    # Define the path to save the QR code image
    qr_code_filename = f'qr_code_{user.username}.png'
    qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_code_filename)
    qr_code_url = os.path.join(settings.MEDIA_URL, 'qr_codes', qr_code_filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)

    # Save the QR code image to the specified path
    with open(qr_code_path, 'wb') as f:
        f.write(qr_code_buffer.read())

    logger.info(f"QR code saved at: {qr_code_path}")

    # Return the URL of the QR code image
    return JsonResponse({'qr_code_url': qr_code_url})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    token = request.data.get('token')
    user = request.user
    logger.debug(f"Username for 2FA: {user.username}")

    try:
        totp_device = TOTPDevice.objects.get(user=user, name='default')
        secret = base64.b32encode(totp_device.bin_key).decode('utf-8')
        logger.debug(f"Token received: {token}")
        logger.debug(f"Shared Secret: {secret}")
        logger.debug(f"Current server time: {datetime.now()}")

        totp = pyotp.TOTP(secret)
        pyotp_verified = totp.verify(token, valid_window=1)
        logger.debug(f"pyotp verification result: {pyotp_verified}")

        if pyotp_verified:
            user.is_2fa_completed = True  # Mark 2FA as completed
            user.save()

            # Generate new JWT tokens with is_2fa_completed attribute
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access['is_2fa_completed'] = True  # Add is_2fa_completed to access token

            logger.info(f"User {user.username} 2FA verified successfully.")
            return Response({
                'message': '2FA verified successfully',
                'refresh': str(refresh),
                'access': str(access)
            })
        else:
            logger.warning(f"Invalid token for user {user.username}.")
            return Response({'error': 'Invalid token'}, status=400)
    except TOTPDevice.DoesNotExist:
        logger.error(f"TOTP device not found for the user: {user.username}")
        return Response({'error': 'TOTP device not found for the user'}, status=400)
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return Response({'error': str(e)}, status=500)

class UserRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User Created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)
