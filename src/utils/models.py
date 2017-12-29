from django.db import models
from django.utils import timezone

from .fields import AutoDateTimeField


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-managed timezone-aware
    "created" and "modified" fields.
    """
    created = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    modified = AutoDateTimeField(default=timezone.now, editable=False)

    class Meta:
        abstract = True
