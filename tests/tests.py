from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase

from .models import Person


class BulkUpdateTests(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)  # mysql doesn't do microseconds. # NOQA
        Person.objects.bulk_create(Person(**person) for person in [
            {
                'big_age': 59999999999999999, 'comma_separated_age': '1,2,3',
                'age': -99, 'positive_age': 9999, 'positive_small_age': 299,
                'small_age': -299, 'name': 'Mike', 'height': Decimal('1.81'),
                'certified': None, 'created': self.now,
                'email': 'miketakeahike@mailinator.com',
            },
            {
                'big_age': 245999992349999, 'comma_separated_age': '6,2,9',
                'age': 25, 'positive_age': 49999, 'positive_small_age': 315,
                'small_age': 5409, 'name': 'Pete', 'height': Decimal('1.93'),
                'certified': True, 'created': self.now,
                'email': 'petekweetookniet@mailinator.com',
            },
            {
                'big_age': 9929992349999, 'comma_separated_age': '6,2,9,10,5',
                'age': 29, 'positive_age': 412399, 'positive_small_age': 23315,
                'small_age': -5409, 'name': 'Ash', 'height': Decimal('1.78'),
                'certified': True, 'created': self.now,
                'email': 'rashash@mailinator.com',
            },
            {
                'big_age': 9992349234, 'comma_separated_age': '12,29,10,5',
                'age': -29, 'positive_age': 4199, 'positive_small_age': 115,
                'small_age': 909, 'name': 'Mary', 'height': Decimal('1.65'),
                'certified': False, 'created': self.now,
                'email': 'marykrismas@mailinator.com',
            },
            {
                'big_age': 999234, 'comma_separated_age': '12,1,30,50',
                'age': 1, 'positive_age': 99199, 'positive_small_age': 5,
                'small_age': -909, 'name': 'Sandra', 'height': Decimal('1.59'),
                'certified': False, 'created': self.now,
                'email': 'sandrasalamandra@mailinator.com',
            },
            {
                'big_age': 9999999999, 'comma_separated_age': '1,100,3,5',
                'age': 35, 'positive_age': 1111, 'positive_small_age': 500,
                'small_age': 110, 'name': 'Crystal', 'height': Decimal('1.71'),
                'certified': None, 'created': self.now,
                'email': 'crystalpalace@mailinator.com',
            },
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

    def test_big_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.big_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.big_age, idx + 27)
            self.assertNotEqual(person.age, person.age + 3)

    def test_comma_separated_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.comma_separated_age = str(idx) + ',27'
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.comma_separated_age, str(idx) + ',27')
            self.assertNotEqual(person.big_age, person.big_age + 3)

    def test_integer_field(self):
        """
            Positive-int values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.age, idx + 27)
            self.assertNotEqual(person.small_age, person.small_age + 3)

    def test_positive_integer_field(self):
        """
            Positive-int values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.positive_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.positive_age, idx + 27)
            self.assertNotEqual(person.small_age, person.small_age + 3)

    def test_positive_small_integer_field(self):
        """
            Positive-int values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.positive_small_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.positive_small_age, idx + 27)
            self.assertNotEqual(person.small_age, person.small_age + 3)

    def test_small_integer_field(self):
        """
            Positive-int values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.small_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.small_age, idx + 27)
            self.assertNotEqual(person.age, person.age + 3)

    def test_datetime(self):
        """
            Datetime values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.created = self.now - timedelta(days=1 + idx)
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.created,
                             self.now - timedelta(days=1 + idx))

    def test_decimal(self):
        """
            Decimal values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.height = Decimal('1.%s' % (50 + idx * 7))
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.height, Decimal('1.%s' % (50 + idx * 7)))

    def test_email(self):
        """
            Email values are saved correctly
        """

        emails = ['walter@mailinator.com', 'thedude@mailinator.com',
                  'donny@mailinator.com', 'jesus@mailinator.com',
                  'buddha@mailinator.com', 'clark@mailinator.com']
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
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age += 1
            person.height += Decimal('0.01')
        Person.objects.bulk_update(people, exclude_fields=['age'])

        people2 = Person.objects.order_by('pk').all()
        for person1, person2 in zip(people, people2):
            self.assertNotEqual(person1.age, person2.age)
            self.assertEqual(person1.height, person2.height)
