from ..users.permissions import IsAdmin
from .permissions import IsOwnerOrReadOnly
from rest_framework import viewsets
from .models import Category, Media, Comment, View
from .serializers import CategorySerializer, MediaSerializer, CommentSerializer, ViewSerializer

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