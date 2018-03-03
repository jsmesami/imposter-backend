import os
import json

from django.conf import settings
from django.core.management import BaseCommand


from imposter.models.posterspec import PosterSpec


class Command(BaseCommand):

    PATH = os.path.join(settings.BASE_DIR, 'specs')
    help = "Populates database with specs from within {path} directory.".format(path=PATH)

    def handle(self, *args, **options):
        for f in sorted(entry.path for entry in os.scandir(self.PATH) if entry.is_file()):
            with open(f) as specs_file:
                data = json.load(specs_file)

                spec_name = data['name']
                spec_instance, created = PosterSpec.objects.get_or_create(name=spec_name, defaults=data)

                print(("Spec '{name}' created" if created else "Spec '{name}' exists, skipped.").format(name=spec_name))
