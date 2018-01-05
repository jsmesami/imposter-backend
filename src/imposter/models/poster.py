import datetime
import os

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.files.base import ContentFile
from django.db import models

from imposter.generator import render_pdf, render_jpg
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
        _, extension = os.path.splitext(filename)

        return 'posters/{filename}{extension}'.format(
            filename='{id:05d}_{bureau.abbrev}_{title}_{created}'.format(
                p=self,
                id=self.id,
                bureau=self.bureau,
                title=self.title,
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

    def save(self, **kwargs):
        self.saved_fields = PosterImage.save_images_from_fields(deepmerge(self.saved_fields, self.spec.editable_fields))

        super().save(**kwargs)  # Save to get the poster ID

        pdf = render_pdf()
        self.print = ContentFile(pdf, name='dummy.pdf')

        thumb = render_jpg(pdf)
        self.thumb = ContentFile(thumb, name='dummy.jpeg')

        super().save(force_update=True)
