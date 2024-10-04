from .models import Topic,ImportantPerson
def create_or_get_topic(topic_data):
    if isinstance(topic_data, str):
        topic, created = Topic.objects.get_or_create(name=topic_data)
        return topic, None
    return None, "Invalid topic data provided"

def create_or_get_important_person(person_data):
    if isinstance(person_data, str):
        person, created = ImportantPerson.objects.get_or_create(name=person_data)
        return person, None
    return None, "Invalid important person data provided"
