import base64
import binascii
import os

from collections import defaultdict
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from utils.functional import deepmerge
from utils.models import TimeStampedModel


class ImageError(Exception):
    pass


class Image(TimeStampedModel):

    BASE_PATH = 'images'
    CORRECT_EXTENSIONS = '.jpeg', '.jpg'

    def _upload_to(self, filename):
        name, extension = os.path.splitext(filename)
        return '{path}/{hash}_{filename}{extension}'.format(
            path=self.BASE_PATH,
            hash=uuid4().hex[:16],
            filename=slugify(name),
            extension=extension,
        )

    file = models.ImageField(upload_to=_upload_to)

    @classmethod
    def normalize_data(cls, image_data, filename):
        if image_data is None:  # Ignoring already saved fields
            return None

        if not isinstance(image_data, str):
            raise ImageError('Image data must be a string.')

        if 'data:' in image_data and ';base64,' in image_data:
            header, image_data = image_data.split(';base64,')
            ext = header.split('/')[-1]
            if '.' + ext not in cls.CORRECT_EXTENSIONS:
                raise ImageError('Unsupported image extension: ' + filename)

        if len(image_data) > settings.UPLOADED_FILE_MAX_SIZE:
            raise ImageError('Image exceeds maximum file size: ' + filename)

        if not image_data:
            raise ImageError('No image data.')

        return image_data

    @classmethod
    def _from_data(cls, image_data, filename):
        path, ext = os.path.splitext(filename)

        if ext not in cls.CORRECT_EXTENSIONS:
            raise ImageError('Unsupported image extension: ' + filename)

        try:
            return cls(file=ContentFile(base64.b64decode(image_data), name=filename))
        except binascii.Error:
            raise ImageError("Can't decode image data: " + filename)

    @classmethod
    def _from_field(cls, field_values):
        existing_image_id = field_values.get('id')
        filename = field_values.get('filename')
        new_image_data = cls.normalize_data(field_values.get('data'), filename)

        if existing_image_id:
            try:
                image = cls.objects.get(pk=existing_image_id)
                if new_image_data:
                    image.delete()
                else:
                    return image
            except cls.DoesNotExist:
                pass

        image = cls._from_data(new_image_data, filename)
        image.save()

        return image

    @classmethod
    def save_images_from_fields(cls, fields):
        """Given fields, save Image objects and return fields with transformed image data."""

        def transform_image_fields(source_fields):
            transformed_fields = defaultdict(dict)
            for field_name, field_values in source_fields.items():
                children = field_values.get('fields')
                if children:
                    transformed_fields[field_name]['fields'] = transform_image_fields(children)
                else:
                    image = cls._from_field(field_values)
                    transformed_fields[field_name]['data'] = None
                    transformed_fields[field_name]['id'] = image.pk
                    transformed_fields[field_name]['filename'] = None
                    transformed_fields[field_name]['url'] = image.file.url
            return transformed_fields

        from imposter.models.posterspec import PosterSpec

        return deepmerge(transform_image_fields(PosterSpec.get_image_fields(fields)), fields)

    class Meta:
        abstract = True


class SpecImage(Image):

    BASE_PATH = 'specs/images'


class PosterImage(Image):

    BASE_PATH = 'posters/images'
