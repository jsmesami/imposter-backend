import datetime
import os

from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from imposter.models.bureau import Bureau
from imposter.models.image import PosterImage
from imposter.models.posterspec import PosterSpec
from utils.functional import deepmerge
from utils.models import TimeStampedModel


class Poster(TimeStampedModel):

    bureau = models.ForeignKey(Bureau, on_delete=models.CASCADE, related_name='posters')
    spec = models.ForeignKey(PosterSpec, on_delete=models.CASCADE, related_name='posters')
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
        return datetime.datetime.today().date() == self.created.date()

    @property
    def title(self):
        return (self.saved_fields.get('title', {}).get('text') or
                "Poster {self.id} ({self.spec.name})".format(self=self))

    def generate_print(self):
        return "TODO"

    def generate_thumb(self):
        return self.print

    def save(self, **kwargs):
        self.print = self.generate_print()
        self.thumb = self.generate_thumb()

        self.saved_fields = PosterImage.save_images_from_fields(deepmerge(self.saved_fields, self.spec.editable_fields))

        super().save(**kwargs)


def walk_fields(fields):
    for field, values in fields.items():
        if 'fields' in values:
            yield from walk_fields(values['fields'])
        else:
            yield values
