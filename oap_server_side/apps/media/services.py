# services.py
from .serializers import MediaSerializer, CategorySerializer

def create_media_with_category(media_data, category_data=None):
    #get category and check if it is dictionary, if it is then create new category 

    if isinstance(category_data, dict):
        category_serializer = CategorySerializer(data=category_data)
        if category_serializer.is_valid():
            category = category_serializer.save()
            media_data['categoryID'] = category.id
        else:
            return None, category_serializer.errors

    media_serializer = MediaSerializer(data=media_data)
    if media_serializer.is_valid():
        media = media_serializer.save()
        return media, None
    return None, media_serializer.errors


    