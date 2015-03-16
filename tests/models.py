from django.db import models

from bulk_update.manager import BulkUpdateManager


class Person(models.Model):
    """
        test model
    """
    # integers
    big_age = models.BigIntegerField()
    comma_separated_age = models.CommaSeparatedIntegerField(max_length=255)
    age = models.IntegerField()
    positive_age = models.PositiveIntegerField()
    positive_small_age = models.PositiveSmallIntegerField()
    small_age = models.SmallIntegerField()

    name = models.fields.CharField(max_length=140, blank=True, null=True)
    height = models.DecimalField(max_digits=3, decimal_places=2)
    email = models.EmailField()
    certified = models.NullBooleanField()
    created = models.fields.DateTimeField(blank=True, null=True)

    objects = BulkUpdateManager()
