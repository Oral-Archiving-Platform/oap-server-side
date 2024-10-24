from .models import City, Monument, Topic, ImportantPerson
from .serializers import CitySerializer, MonumentSerializer


def create_or_get_city(city_data):
    if isinstance(city_data, int):
        try:
            city = City.objects.get(id=city_data)
            return city, None
        except City.DoesNotExist:
            return None, f"City with ID {city_data} does not exist."
    
    elif isinstance(city_data, dict):
        serializer = CitySerializer(data=city_data)
        if serializer.is_valid():
            city=serializer.save()
            return city, None
        else:
            return None, serializer.errors
    return None, "Invalid city data format."


def create_or_get_monument(monument_data):
    if isinstance(monument_data, int):
        try:
            monument = Monument.objects.get(id=monument_data)
            return monument, None
        except Monument.DoesNotExist:
            return None, f"Monument with ID {monument_data} does not exist."
    
    elif isinstance(monument_data, dict):
        city_data = monument_data.get('city')
        print("hoh city data")
        if not city_data:
            return None, "A city must be provided for the monument."

        city, city_error = create_or_get_city(city_data)
        if city_error:
            return None, city_error
        print("cyrr")
        monument_data["city"] = city.id
        serializer = MonumentSerializer(data=monument_data)
        if serializer.is_valid():
            monument = serializer.save()
            return monument, None
        else:
            return None, serializer.errors
    else:
        return None, "Invalid monument data format."
