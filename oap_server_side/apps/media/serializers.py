from rest_framework import serializers
from .models import Category, Media, Comment, View

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, required=False)
    class Meta:
        model = Comment
        fields = '__all__'

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