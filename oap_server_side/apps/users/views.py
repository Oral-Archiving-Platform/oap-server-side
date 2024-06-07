# Necessary imports for authentication
from rest_framework.views import APIView
from rest_framework import status,viewsets

from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import action

from rest_framework.permissions import AllowAny, IsAuthenticated


from .models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, TokenError



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class VerifyTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'valid': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_role(self, request):
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
    

