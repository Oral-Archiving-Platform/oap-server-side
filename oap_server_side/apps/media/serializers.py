from rest_framework import serializers
from .models import Category, Media, Comment, View, Like,OriginalLanguage


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['userID']


class MediaSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()#add a new field to the serializer read-only ,calls a method on the serializer class it is attached to.
    views = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()  # Add this field


    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ['uploadDate']



    def get_likes(self, obj):
        return Like.objects.filter(mediaID=obj).count()
    
    def get_views(self, obj):
        return View.objects.filter(mediaID=obj).count()
    
    def get_category_name(self, obj):
        return obj.categoryID.name
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
class OriginalLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalLanguage
        fields = '__all__'

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
    
=======
    username = serializers.CharField(source='userID.username', read_only=True)
>>>>>>> origin/fatima
    replies = RecursiveField(many=True, required=False)
    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['userID']
    def get_firstName(self, obj):
        return obj.userID.first_name
    def get_lastName(self, obj):
        return obj.userID.last_name

    def validate(self, data):
        if 'parent' in data and data['parent'] is not None:
            if data['parent'].mediaID != data['mediaID']:
                raise serializers.ValidationError('Parent comment must belong to the same media.')
        return data

    def update(self, instance, validated_data):
        if 'parent' in validated_data:
            raise serializers.ValidationError('Cannot change the parent of a comment.')
        return super().update(instance, validated_data)

class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = '__all__'
        read_only_fields = ['userID']
