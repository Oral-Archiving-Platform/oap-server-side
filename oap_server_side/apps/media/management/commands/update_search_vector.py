from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from apps.media.models import Media

class Command(BaseCommand):
    help = 'Update search vector for Media'

    def handle(self, *args, **kwargs):
        Media.objects.update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('description', weight='B')
            )
        )
        self.stdout.write(self.style.SUCCESS('Successfully updated search vector for Media'))