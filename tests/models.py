from django.db import models
from bulk_update.manager import BulkUpdateManager

class Person(models.Model):
    """
        test model
    """
    name      = models.fields.CharField(max_length=140, blank=True, null=True)
    age       = models.PositiveIntegerField()
    height    = models.DecimalField(max_digits=3, decimal_places=2)
    email     = models.EmailField()
    certified = models.NullBooleanField()
    created   = models.fields.DateTimeField(blank=True, null=True)

    objects = BulkUpdateManager()
