import base64
import os

from collections import defaultdict
from uuid import uuid4

from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from utils.functional import deepmerge
from utils.models import TimeStampedModel

from imposter.models.poster import Poster, PosterSpec


class Image(TimeStampedModel):

    BASE_PATH = 'images'

    def _upload_to(self, filename):
        name, extension = os.path.splitext(filename)
        return '{path}/{hash}_{filename}{extension}'.format(
            path=self.BASE_PATH,
            hash=uuid4().hex[:16],
            filename=slugify(name),
            extension=extension,
        )

    file = models.ImageField(upload_to=_upload_to)

    @staticmethod
    def normalize_data(image_data):
        if not isinstance(image_data, str):
            raise ValueError('Image data must be string.')

        if 'data:' in image_data and ';base64,' in image_data:
            header, image_data = image_data.split(';base64,')

        return image_data

    @classmethod
    def from_data(cls, image_data, filename, **kwargs):
        return cls(
            file=ContentFile(base64.b64decode(image_data), name=filename),
            **kwargs
        )

    @classmethod
    def _from_field(cls, field_values, **kwargs):
        existing_image_id = field_values.get('id')
        new_image_data = cls.normalize_data(field_values.get('data'))

        if existing_image_id:
            try:
                image = cls.objects.get(pk=existing_image_id)
                if new_image_data:
                    image.delete()
                else:
                    return image
            except cls.DoesNotExist:
                pass

        image = cls.from_data(new_image_data, field_values.get('filename'), **kwargs)
        image.save()

        return image

    @classmethod
    def save_images_from_fields(cls, fields, **kwargs):
        """Given fields, save Image objects and return fields with transformed image data."""

        def transform(source_fields):
            transformed_fields = defaultdict(dict)
            for field_name, field_values in source_fields.items():
                children = field_values.get('fields')
                if children:
                    transformed_fields[field_name]['fields'] = transform(children)
                else:
                    image = cls._from_field(field_values, **kwargs)
                    transformed_fields[field_name]['data'] = None
                    transformed_fields[field_name]['id'] = image.pk
                    transformed_fields[field_name]['filename'] = None
                    transformed_fields[field_name]['url'] = image.file.url
            return transformed_fields

        return deepmerge(transform(PosterSpec.get_image_fields(fields)), fields)

    class Meta:
        abstract = True


class SpecImage(Image):

    BASE_PATH = 'specs/images'
    spec = models.ForeignKey(PosterSpec, on_delete=models.CASCADE, related_name='images')


class PosterImage(Image):

    BASE_PATH = 'posters/images'
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, related_name='images')
