from .serializers import MediaSerializer, CategorySerializer

from .models import Category, Media
from .serializers import CategorySerializer, MediaSerializer

def create_media_with_category(media_data, category_data=None):
    # Get or create category
    if isinstance(category_data, dict):
        category_name = category_data.get('name')
        print("Category Name:", category_name)
        category, created = Category.objects.get_or_create(name=category_name)
        media_data['categoryID'] = category.id
    elif isinstance(category_data, str):  # Assuming category_data can also be a string for category name
        category, created = Category.objects.get_or_create(name=category_data)
        media_data['categoryID'] = category.id
    else:
        return None, "Invalid category data provided"

    print("Media Data:", media_data)

    # Create media with that category
    media_serializer = MediaSerializer(data=media_data)
    if media_serializer.is_valid():
        media = media_serializer.save()
        return media, None
    return None, media_serializer.errors
