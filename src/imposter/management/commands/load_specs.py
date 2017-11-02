import os
import json
from copy import deepcopy

from django.conf import settings
from django.core.management import BaseCommand


from imposter.models import PosterSpec, SpecImage
from utils.functional import deepmerge


class Command(BaseCommand):

    def handle(self, *args, **options):
        specs_path = os.path.join(settings.BASE_DIR, 'specs')

        for f in (entry.path for entry in os.scandir(specs_path) if entry.is_file()):
            with open(f) as spec_file:
                specs_data = json.load(spec_file)
                fields_copy = deepcopy(specs_data['fields'])

                specs_data['fields'] = {}  # Save stub only, we are going to add transformed data later.
                spec_instance, created = PosterSpec.objects.get_or_create(
                    name=specs_data['name'],
                    defaults=specs_data)

                spec_instance.images.all().delete()
                transformed_fields = SpecImage.save_images_from_fields(
                    PosterSpec.get_static_fields(fields_copy),
                    spec=spec_instance)

                spec_instance.fields = deepmerge(transformed_fields, fields_copy)
                spec_instance.save()
