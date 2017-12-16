import os
import json

from django.conf import settings
from django.core.management import BaseCommand


from imposter.models.posterspec import PosterSpec


class Command(BaseCommand):

    def handle(self, *args, **options):
        specs_path = os.path.join(settings.BASE_DIR, 'specs')

        for f in (entry.path for entry in os.scandir(specs_path) if entry.is_file()):
            with open(f) as specs_file:
                data = json.load(specs_file)

                spec_name = data['name']
                spec_instance, created = PosterSpec.objects.get_or_create(name=spec_name, defaults=data)

                print(("Spec '{}' created" if created else "Spec '{}' exists, skipped.").format(spec_name))
