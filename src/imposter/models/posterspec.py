import base64

from collections import OrderedDict

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from imposter.models import EnabledQuerySet
from utils.models import TimeStampedModel


class PosterSpec(TimeStampedModel):
    """
    Provides specification (template) for poster creation
    """

    name = models.CharField(max_length=255, unique=True)
    w = models.PositiveIntegerField()
    h = models.PositiveIntegerField()
    color = models.CharField(max_length=7)  # Distinguishing color code as a HEX triplet (eg. '#00FF00')
    thumb = models.ImageField(upload_to='specs/thumbs')
    frames = JSONField()
    static_fields = JSONField()
    editable_fields = JSONField()
    disabled = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(EnabledQuerySet)()

    ALLOWED_FIELD_PARAMS = {
        'text': {'text'},
        'image': {'filename', 'data'},
    }

    @staticmethod
    def get_text_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('type') == 'text')

    @staticmethod
    def get_image_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('type') == 'image')

    @staticmethod
    def get_mandatory_fields(fields):
        return OrderedDict((k, v) for k, v in fields.items() if v.get('mandatory'))

    def save(self, **kwargs):
        from imposter.models.image import SpecImage

        thumb_name = slugify(self.name)+'-thumb.jpg'
        thumb_data = SpecImage.normalize_data(str(self.thumb), thumb_name)
        self.thumb = ContentFile(base64.b64decode(thumb_data), name=thumb_name)

        self.static_fields = SpecImage.save_images_from_fields(self.static_fields)

        super().save(**kwargs)
