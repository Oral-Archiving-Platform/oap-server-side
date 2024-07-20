from ..users.permissions import IsAdmin
from .permissions import IsOwnerOrReadOnly
from rest_framework import viewsets
from .models import Category, Media, Comment, View
from .serializers import CategorySerializer, MediaSerializer, CommentSerializer, ViewSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import View
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import View

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin,IsOwnerOrReadOnly]


class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin,IsOwnerOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class ViewViewSet(viewsets.ModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer

class UserActivityViewSet(viewsets.ViewSet):
    queryset = View.objects.all()  # Define the queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='list-viewing-history/(?P<user_id>\d+)')
    def list_viewing_history(self, request, user_id=None):
        """Retrieve the viewing history of a specific user."""
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        views = View.objects.filter(userID=user_id)
        serializer = ViewSerializer(views, many=True)
        return Response({"user_id": user_id, "history": serializer.data})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='create-video-view-history')
    def create_video_view_history(self, request, pk=None):
        """Create or update the viewing history for a specific user."""
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Use the user ID from URL
        userID = pk
        
        # Validate and process request data
        serializer = ViewSerializer(data=request.data)
        if serializer.is_valid():
            userID=serializer.validated_data['userID']
            mediaID = serializer.validated_data['mediaID']
            viewed_at = serializer.validated_data['viewDate']
            
            # Create or update the viewing history
            try:
                View.objects.create(userID=userID, mediaID=mediaID, viewDate=viewed_at)
                return Response({"success": True, "message": "Video history updated successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)