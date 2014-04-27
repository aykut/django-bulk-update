from django.db import models
from . import bulk_update


class BulkUpdateManager(models.Manager):
    def bulk_update(self, objs, update_fields=None, exclude_fields=None):
        bulk_update(objs, update_fields=update_fields,
                    exclude_fields=exclude_fields, using=self.db)
