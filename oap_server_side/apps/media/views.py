from ..users.permissions import IsAdmin
from .permissions import IsOwnerOrReadOnly
from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Category, Media, Comment, View
from .serializers import CategorySerializer, MediaSerializer, CommentSerializer, ViewSerializer
from .services import create_media_with_category

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin,IsOwnerOrReadOnly]


class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin,IsOwnerOrReadOnly]
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def create(self, request, *args, **kwargs):
        #use a service to create media with category
        media, errors = create_media_with_category(request.data, request.data.get('categoryID'))
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(MediaSerializer(media).data, status=status.HTTP_201_CREATED)
        
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class ViewViewSet(viewsets.ModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer