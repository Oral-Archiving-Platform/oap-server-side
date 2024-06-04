# Necessary imports for authentication
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.timezone import now
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import viewsets

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions


# views.py
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, UserInfoSerializer
from rest_framework_simplejwt.tokens import AccessToken, TokenError

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserInfoSerializer
        return UserSerializer
    
class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):

        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class VerifyTokenView(APIView):
    permission_classes = (AllowAny,)

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
        """
        Returns the user role based on the provided authorization token.
        """
        # Access token from the request's authorization header (Bearer token)
        token = request.headers.get('Authorization', None)
        if not token:
            return Response({'error': 'Authorization token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Split the token to remove the bearer prefix
            token = token.split(' ')[1]
            # Decode and validate the token
            decoded_token = AccessToken(token)
            # Extract user role from the token
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

        # Add custom claims
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['id'] = user.id
        token['role'] = user.role
        token['picture'] = user.picture.url if user.picture else None
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserRegister(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User Created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TestView(APIView):
    queryset = User.objects.all()

    def get(self, request):
        return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)