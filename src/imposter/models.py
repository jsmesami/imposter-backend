import base64
import os
from collections import OrderedDict, defaultdict
from uuid import uuid4

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from utils.functional import deepmerge
from utils.models import TimeStampedModel


class EnabledQuerySet(models.QuerySet):

    def enabled(self):
        return self.filter(disabled=False)


class Bureau(models.Model):

    name = models.CharField(max_length=255)
    abbrev = models.CharField(max_length=8)
    number = models.PositiveSmallIntegerField()
    address = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(EnabledQuerySet)()


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

    FIELD_SPECS = {
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


class Poster(TimeStampedModel):

    bureau = models.ForeignKey(Bureau, related_name='posters')
    spec = models.ForeignKey(PosterSpec, related_name='posters')
    saved_fields = JSONField(editable=False)  # Fields from spec with saved values

    def _upload_to(self, filename):
        name_template = '{p.id:05d}_{p.bureau.number:02d}_{p.bureau.abbrev}_{p.spec.title}_{created}'
        _, extension = os.path.splitext(filename)
        return 'posters/{filename}.{extension}'.format(
            filename=name_template.format(
                p=self,
                created='{d:02d}{m:02d}{y}'.format(
                    d=self.created.day,
                    m=self.created.month,
                    y=str(self.created.year)[-2:],
                ),
            ),
            extension=extension,
        )

    thumb = models.ImageField(upload_to=_upload_to, editable=False)
    print = models.FileField(upload_to=_upload_to, editable=False)

    @property
    def editable(self):
        """Poster is editable only the day it was created."""
        return self.modified.date() == self.created.date()

    @property
    def title(self):
        return (self.saved_fields.get('title', {}).get('text') or
                "Plakát {self.id} ({self.spec.name})".format(self=self))

    def generate_print(self):
        return "TODO"

    def generate_thumb(self):
        return self.print

    def save(self, **kwargs):
        self.print = self.generate_print()
        self.thumb = self.generate_thumb()
        super().save(**kwargs)


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
    def decode_base64(data):
        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            return base64.b64decode(data)

    @classmethod
    def from_data(cls, data, filename, **kwargs):
        return cls(
            file=ContentFile(cls.decode_base64(data), name=filename),
            **kwargs
        )

    @classmethod
    def save_images_from_fields(cls, fields, **kwargs):
        """Given spec fields, save Image objects and return transformed specs to be saved with PosterSpec object"""

        def transform(source_fields):
            transformed_fields = defaultdict(dict)
            for field_name, field_specs in source_fields.items():
                children = field_specs.get('fields')
                if children:
                    transformed_fields[field_name]['fields'] = transform(children)
                else:
                    image = cls.from_data(field_specs['data'], field_specs['filename'], **kwargs)
                    image.save()
                    transformed_fields[field_name]['data'] = ''
                    transformed_fields[field_name]['filename'] = image.file.name
            return transformed_fields

        return deepmerge(transform(PosterSpec.get_image_fields(fields)), fields)

    class Meta:
        abstract = True


class SpecImage(Image):

    BASE_PATH = 'specs/images'
    spec = models.ForeignKey(PosterSpec, related_name='images')


class PosterImage(Image):

    BASE_PATH = 'posters/images'
    poster = models.ForeignKey(Poster, related_name='images')
