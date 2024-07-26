from ..users.permissions import IsAdmin
from .permissions import IsOwnerOrReadOnly,IsChannelMemberOrReadOnly
from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Category, Media, Comment, View, Like
from .serializers import CategorySerializer, MediaSerializer, CommentSerializer, ViewSerializer, LikeSerializer
from .services import create_media_with_category
from django.db import transaction
from ..video.models import Video
from rest_framework.decorators import action


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin,IsOwnerOrReadOnly]


class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin,IsOwnerOrReadOnly,IsChannelMemberOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def create(self, request, *args, **kwargs):
        #use a service to create media with category
        with transaction.atomic():

            media, errors = create_media_with_category(request.data, request.data.get('categoryID'))
            if errors:
                transaction.set_rollback(True)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(MediaSerializer(media).data, status=status.HTTP_201_CREATED)
            
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    #to remove if you want replies to show also as independent instances:
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
