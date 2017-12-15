import base64
import os
import json
from copy import deepcopy

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management import BaseCommand


from imposter.models.posterspec import PosterSpec
from imposter.models.image import SpecImage
from utils.functional import deepmerge


class Command(BaseCommand):

    def handle(self, *args, **options):
        specs_path = os.path.join(settings.BASE_DIR, 'specs')

        for f in (entry.path for entry in os.scandir(specs_path) if entry.is_file()):
            with open(f) as spec_file:
                specs_data = json.load(spec_file)

                thumb_data = specs_data['thumb']
                specs_data['thumb'] = ''

                fields_copy = deepcopy(specs_data['fields'])
                specs_data['fields'] = {}  # Save empty, we are going to add transformed data later.

                spec_name = specs_data['name']
                spec_instance, created = PosterSpec.objects.get_or_create(
                    name=spec_name,
                    defaults=specs_data)

                if created:
                    transformed_fields = SpecImage.save_images_from_fields(
                        PosterSpec.get_static_fields(fields_copy),
                        spec=spec_instance
                    )

                    thumb_data = SpecImage.normalize_data(thumb_data)
                    thumb_name, _ = os.path.splitext(os.path.basename(f))
                    spec_instance.thumb = ContentFile(base64.b64decode(thumb_data), name=thumb_name+'.jpg')

                    spec_instance.fields = deepmerge(transformed_fields, fields_copy)
                    spec_instance.save()

                    print("Spec '{}' created".format(spec_name))
                else:
                    print("Spec '{}' exists, skipped.".format(spec_name))
