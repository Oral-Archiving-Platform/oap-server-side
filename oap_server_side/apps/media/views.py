from ..users.permissions import IsAdmin
from .permissions import IsOwnerOrReadOnly
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category, Media, Comment, View, Like
from .serializers import CategorySerializer, MediaSerializer, CommentSerializer, ViewSerializer, LikeSerializer
from .services import create_media_with_category
from django.db import transaction
from ..video.models import Video
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin, IsOwnerOrReadOnly]

class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin, IsOwnerOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def create(self, request, *args, **kwargs):
        # Use a service to create media with category
        with transaction.atomic():
            media, errors = create_media_with_category(request.data, request.data.get('categoryID'))
            if errors:
                transaction.set_rollback(True)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(MediaSerializer(media).data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # To remove if you want replies to show also as independent instances:
    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True)
    
    def perform_create(self, serializer):
        serializer.save(userID=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-video/(?P<video_id>[^/.]+)')
    def get_comments_by_video(self, request, video_id=None):
        try:
            video = Video.objects.get(id=video_id)
            comments = Comment.objects.filter(mediaID=video.mediaID, parent__isnull=True)
            serializer = self.get_serializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response({'detail': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

class ViewViewSet(viewsets.ModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer

    def perform_create(self, serializer):
        serializer.save(userID=self.request.user)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        serializer.save(userID=self.request.user)

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
            userID = serializer.validated_data['userID']
            mediaID = serializer.validated_data['mediaID']
            viewed_at = serializer.validated_data['viewDate']
            
            # Create or update the viewing history
            try:
                View.objects.create(userID=userID, mediaID=mediaID, viewDate=viewed_at)
                return Response({"success": True, "message": "Video history updated successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
