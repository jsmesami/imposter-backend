import base64
import binascii
import os

from collections import defaultdict
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from utils.functional import deepmerge
from utils.models import TimeStampedModel


class ImageError(Exception):
    pass


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
    def normalize_data(image_data, filename):
        if image_data is None:  # Ignoring already saved fields
            return None

        if not isinstance(image_data, str):
            raise ImageError(_('Image data must be a string.'))

        if 'data:' in image_data and ';base64,' in image_data:
            header, image_data = image_data.split(';base64,')
            ext = header.split('/')[-1]
            if '.' + ext not in settings.SUPPORTED_IMAGE_EXTENSIONS:
                raise ImageError(_('Unsupported image file extension: {filename}').format(filename=filename))

        if len(image_data) > settings.UPLOADED_FILE_MAX_SIZE:
            raise ImageError(_('Image exceeds maximum file size: {filename}').format(filename=filename))

        if not image_data:
            raise ImageError(_('No image data.'))

        return image_data

    @classmethod
    def _from_data(cls, image_data, filename):
        path, ext = os.path.splitext(filename)

        if ext not in settings.SUPPORTED_IMAGE_EXTENSIONS:
            raise ImageError(_('Unsupported image file extension: {filename}').format(filename=filename))

        try:
            return cls(file=ContentFile(base64.b64decode(image_data), name=filename))
        except binascii.Error:
            raise ImageError(_("Can't decode image data: {filename}").format(filename=filename))

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
        """
        Within fields, substitute base64-encoded images for urls to image files saved to disk.
        """
        from imposter.models.posterspec import PosterSpec  # local import because of cross-reference

        transformed_fields = defaultdict(dict)

        for field_name, field_values in PosterSpec.get_image_fields(fields).items():
            image = cls._from_field(field_values)
            transformed_fields[field_name]['data'] = None
            transformed_fields[field_name]['id'] = image.pk
            transformed_fields[field_name]['filename'] = None
            transformed_fields[field_name]['url'] = image.file.url

        return deepmerge(transformed_fields, fields)

    class Meta:
        abstract = True


class SpecImage(Image):

    BASE_PATH = 'specs/images'


class PosterImage(Image):

    BASE_PATH = 'posters/images'
