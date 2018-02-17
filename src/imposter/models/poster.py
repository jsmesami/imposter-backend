import datetime
import os

from unidecode import unidecode

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

from imposter.renderer import Renderer
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
                title=slugify(unidecode(self.title)),
                created='{y}{m:02d}{d:02d}'.format(
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
        """
        Poster editability: poster is editable only the day it was created.
        """
        return datetime.datetime.today().date() == self.created.date()

    @property
    def title(self):
        """
        If fields contain a title, return it, else render something meaningful.
        """
        return (self.saved_fields.get('title', {}).get('text') or
                "Poster {self.id} ({self.spec.name})".format(self=self))

    def save(self, **kwargs):
        # Fields being saved need to be populated with data from spec (not present in request).
        populated_fields = deepmerge(
            self.saved_fields,
            {k: v for (k, v) in self.spec.editable_fields.items() if k in self.saved_fields},
        )

        self.saved_fields = PosterImage.save_images_from_fields(populated_fields)

        # Save to get the poster ID
        super().save(**kwargs)

        renderer = Renderer(self.spec, self.saved_fields)
        pdf = renderer.render_pdf()
        self.print = ContentFile(pdf, name='dummy.pdf')

        thumb = renderer.render_jpg(pdf)
        self.thumb = ContentFile(thumb, name='dummy.jpeg')

        super().save(force_update=True)

    class Meta:
        ordering = '-modified',
