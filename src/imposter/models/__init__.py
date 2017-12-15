from django.db import models


class EnabledQuerySet(models.QuerySet):

    def enabled(self):
        return self.filter(disabled=False)
