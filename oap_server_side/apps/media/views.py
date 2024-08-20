from .permissions import IsChannelMemberOrReadOnly
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
from .models import View
from django.db.models import Q

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [ IsChannelMemberOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            media_data = request.data.copy()
            media_data["uploaderID"] = request.user.id
            media, errors = create_media_with_category(media_data, media_data.get('categoryID'))
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
        user = self.request.user
        media = serializer.validated_data['mediaID']
        existing_like = Like.objects.filter(mediaID=media, userID=user).first()
        
        if existing_like:
            existing_like.delete()
            return Response({'message': 'Like removed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer.save(userID=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    @action(detail=False, methods=['get'], url_path='search')
    def search_media(self, request):
        # Get the search query from request parameters
        query = request.query_params.get('q', '')

        if query:
            # Filter media based on literal matching of title or description
            media_results = Media.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            
            if media_results.exists():
                    # Serialize the results using MediaSerializer
                    serializer = MediaSerializer(media_results, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                    # Return message if no media was found
                return Response({"detail": "No media found matching the search query."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)
