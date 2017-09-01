from django.db import models
from .helper import bulk_update, bulk_update_or_create


class BulkUpdateQuerySet(models.QuerySet):

    def bulk_update(self, objs, update_fields=None,
                    exclude_fields=None, batch_size=None):

        self._for_write = True
        using = self.db

        return bulk_update(
            objs, update_fields=update_fields,
            exclude_fields=exclude_fields, using=using,
            batch_size=batch_size)

    def bulk_update_or_create(self, objs, update_fields=None,
                              exclude_fields=None, batch_size=None, update_choice=None):

        self._for_write = True
        using = self.db

        return bulk_update_or_create(
            objs, update_fields=update_fields,
            exclude_fields=exclude_fields, using=using,
            batch_size=batch_size, update_choice=update_choice
        )
