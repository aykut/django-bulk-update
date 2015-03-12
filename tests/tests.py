from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Person


class BulkUpdateTests(TestCase):
    
    def setUp(self):
        self.now = timezone.now()
        Person.objects.bulk_create(Person(name=name, created=self.now) for name in ['Mike', 'Pete', 'Ash', 'Mary', 'Sandra', 'Crystal'])

    def test_bulk_update(self):
        """
            Basic example of bulk_update usage
        """
        people = Person.objects.order_by('pk').all()
        
        # change names with bulk update
        names = ['Walter', 'The Dude', 'Donny', 'Jesus']
        for idx, person in enumerate(people):
            person.name = names[idx % 4]
        Person.objects.bulk_update(people)
        
        # check that names are set
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.name, names[idx % 4])

    def test_datetime_bulk_update(self):
        """
            Test that datetime values are saved correctly
        """
        
        people = Person.objects.order_by('pk').all()
        
        for idx, person in enumerate(people):
            person.created = self.now - timedelta(days=1+idx)
        Person.objects.bulk_update(people)
        
        for idx, person in enumerate(people):
            self.assertEqual(person.created, self.now - timedelta(days=1+idx))
