from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Person
from decimal import Decimal

class BulkUpdateTests(TestCase):
    
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0) # mysql doesn't do microseconds.
        Person.objects.bulk_create(Person(**person) for person in [
           {'name': 'Mike',    'age': 20, 'height': Decimal('1.81'), 'email': 'miketakeahike@mailinator.com',    'certified': None,  'created': self.now},
           {'name': 'Pete',    'age': 33, 'height': Decimal('1.93'), 'email': 'petekweetookniet@mailinator.com', 'certified': True,  'created': self.now},
           {'name': 'Ash',     'age': 29, 'height': Decimal('1.78'), 'email': 'rashash@mailinator.com',          'certified': True,  'created': self.now},
           {'name': 'Mary',    'age': 25, 'height': Decimal('1.65'), 'email': 'marykrismas@mailinator.com',      'certified': False, 'created': self.now},
           {'name': 'Sandra',  'age': 30, 'height': Decimal('1.59'), 'email': 'sandrasalamandra@mailinator.com', 'certified': False, 'created': self.now},
           {'name': 'Crystal', 'age': 27, 'height': Decimal('1.71'), 'email': 'crystalpalace@mailinator.com',    'certified': None,  'created': self.now},
        ])



    def test_basic_bulk_update(self):
        """
            Basic bulk_update succeeds
        """
        people = Person.objects.order_by('pk').all()
        
        # change names with bulk update
        names = ['Walter', 'The Dude', 'Donny', 'Jesus', 'Buddha', 'Clark']
        for idx, person in enumerate(people):
            person.name = names[idx]
        Person.objects.bulk_update(people)
        
        # check that names are set
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.name, names[idx])

    def test_datetime(self):
        """
            Datetime values are saved correctly
        """
        
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.created = self.now - timedelta(days=1+idx)
        Person.objects.bulk_update(people)
        
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.created, self.now - timedelta(days=1+idx))

    def test_positive_int(self):
        """
            Positive-int values are saved correctly
        """
        
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age = idx+27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.age, idx+27)

    def test_decimal(self):
        """
            Decimal values are saved correctly
        """
        
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.height = Decimal('1.%s' % (50+idx*7))
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.height, Decimal('1.%s' % (50+idx*7)))

    def test_email(self):
        """
            Email values are saved correctly
        """
        
        emails = ['walter@mailinator.com', 'thedude@mailinator.com', 'donny@mailinator.com', 
                  'jesus@mailinator.com', 'buddha@mailinator.com', 'clark@mailinator.com']
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.email = emails[idx]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.email, emails[idx])

    def test_null_boolean(self):
        """
            Null-boolean values are saved correctly
        """
        
        vals = [True, False, None]
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.certified = vals[idx % 3]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.certified, vals[idx % 3])

    def test_update_fields(self):
        """
            Only the fields in "update_fields" are updated
        """
        vals = [True, False, None]
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age += 1
            person.height += Decimal('0.01')
        Person.objects.bulk_update(people, update_fields=['age'])

        people2 = Person.objects.order_by('pk').all()
        for person1, person2 in zip(people, people2):
            self.assertEqual(person1.age, person2.age)
            self.assertNotEqual(person1.height, person2.height)

    def test_exclude_fields(self):
        """
            Only the fields not in "exclude_fields" are updated
        """
        vals = [True, False, None]
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age += 1
            person.height += Decimal('0.01')
        Person.objects.bulk_update(people, exclude_fields=['age'])

        people2 = Person.objects.order_by('pk').all()
        for person1, person2 in zip(people, people2):
            self.assertNotEqual(person1.age, person2.age)
            self.assertEqual(person1.height, person2.height)




   
