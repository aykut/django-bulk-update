from django.db import models
from django.db.models.manager import Manager
from .helper import bulk_update


class BulkUpdateQuerySet(models.QuerySet):
    def bulk_update(self, objs, update_fields=None, exclude_fields=None, batch_size=None):
        self._for_write = True
        return bulk_update(
            objs, update_fields=update_fields,
            exclude_fields=exclude_fields, using=self.db,
            batch_size=batch_size)


class BulkUpdateManager(Manager.from_queryset(BulkUpdateQuerySet)):
    pass
