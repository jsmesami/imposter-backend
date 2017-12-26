import base64

from collections import OrderedDict

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from imposter.models import EnabledQuerySet
from utils.functional import deepmerge
from utils.models import TimeStampedModel


class PosterSpec(TimeStampedModel):
    """Provides specification (template) for poster creation"""

    name = models.CharField(max_length=255, unique=True)
    w = models.PositiveIntegerField()
    h = models.PositiveIntegerField()
    color = models.CharField(max_length=6)  # Distinguishing color code
    thumb = models.ImageField(upload_to='specs/thumbs')
    frames = JSONField()
    fields = JSONField()
    disabled = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(EnabledQuerySet)()

    FIELD_PARAMS = {
        'text': {
            'editable': {'text', 'fields'},
            'mandatory': {'text'},
        },
        'image': {
            'editable': {'filename', 'data', 'fields'},
            'mandatory': {'filename', 'data'},
        }
    }

    @staticmethod
    def get_text_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('type') == 'text')

    @property
    def text_fields(self):
        return self.get_text_fields(self.fields)

    @staticmethod
    def get_image_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('type') == 'image')

    @property
    def image_fields(self):
        return self.get_image_fields(self.fields)

    @staticmethod
    def get_mandatory_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('mandatory'))

    @property
    def mandatory_fields(self):
        return self.get_mandatory_fields(self.fields)

    @staticmethod
    def get_static_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('static'))

    @property
    def static_fields(self):
        return self.get_editable_fields(self.fields)

    @staticmethod
    def get_editable_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if not v.get('static'))

    @property
    def editable_fields(self):
        return self.get_editable_fields(self.fields)

    def save(self, **kwargs):
        from imposter.models.image import SpecImage

        thumb_name = slugify(self.name)+'-thumb.jpg'
        thumb_data = SpecImage.normalize_data(str(self.thumb), thumb_name)
        self.thumb = ContentFile(base64.b64decode(thumb_data), name=thumb_name)

        self.fields = deepmerge(
            SpecImage.save_images_from_fields(self.get_static_fields(self.fields)),
            self.fields,
        )

        super().save(**kwargs)
