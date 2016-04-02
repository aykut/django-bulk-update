from django.db import models
from django.db.models.manager import BaseManager
from .helper import bulk_update


class BulkUpdateQuerySet(models.QuerySet):
    def bulk_update(self, objs, update_fields=None, exclude_fields=None):
        self._for_write = True
        bulk_update(objs, update_fields=update_fields,
                    exclude_fields=exclude_fields, using=self.db)


class BulkUpdateManager(BaseManager.from_queryset(BulkUpdateQuerySet)):
    pass
