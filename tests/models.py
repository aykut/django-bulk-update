from django.db import models

from bulk_update.manager import BulkUpdateManager


class Person(models.Model):
    """
        test model
    """
    big_age = models.BigIntegerField()
    comma_separated_age = models.CommaSeparatedIntegerField(max_length=255)
    age = models.IntegerField()
    positive_age = models.PositiveIntegerField()
    positive_small_age = models.PositiveSmallIntegerField()
    small_age = models.SmallIntegerField()
    height = models.DecimalField(max_digits=3, decimal_places=2)
    float_height = models.FloatField()

    certified = models.BooleanField(default=False)
    null_certified = models.NullBooleanField()

    name = models.CharField(max_length=140, blank=True, null=True)
    email = models.EmailField()
    file_path = models.FilePathField()
    slug = models.SlugField()
    text = models.TextField()
    url = models.URLField()

    date_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    remote_addr = models.GenericIPAddressField(null=True, blank=True)

    my_file = models.FileField(upload_to='/some/path/', null=True, blank=True)
    image = models.ImageField(upload_to='/some/path/', null=True, blank=True)

    objects = BulkUpdateManager()
