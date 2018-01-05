from django.db import models

from imposter.models import EnabledQuerySet


class Bureau(models.Model):

    name = models.CharField(max_length=255)
    abbrev = models.CharField(max_length=8)
    address = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(EnabledQuerySet)()
