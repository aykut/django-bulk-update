from datetime import date, time, timedelta
from decimal import Decimal
import random

from django.test import TestCase
from django.utils import timezone

from .models import Person
from .fixtures import create_fixtures


class BulkUpdateTests(TestCase):

    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)  # mysql doesn't do microseconds. # NOQA
        self.date = date(2015, 3, 28)
        self.time = time(13, 0)
        create_fixtures()

    def test_big_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.big_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.big_age, idx + 27)

    def test_comma_separated_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.comma_separated_age = str(idx) + ',27'
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.comma_separated_age, str(idx) + ',27')

    def test_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.age, idx + 27)

    def test_positive_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.positive_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.positive_age, idx + 27)

    def test_positive_small_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.positive_small_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.positive_small_age, idx + 27)

    def test_small_integer_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.small_age = idx + 27
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.small_age, idx + 27)

    def test_boolean_field(self):
        vals = [True, False, True]
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.certified = vals[idx % 3]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.certified, vals[idx % 3])

    def test_null_boolean_field(self):
        """
            Null-boolean values are saved correctly
        """

        vals = [True, False, None]
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.null_certified = vals[idx % 3]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.null_certified, vals[idx % 3])

    def test_char_field(self):
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

    def test_email_field(self):
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

    def test_file_path_field(self):
        file_paths = ['/home/dummy.txt', '/Downloads/kitten.jpg',
                      '/Users/user/fixtures.json', 'dummy.png',
                      'users.json', '/home/dummy.png']
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.file_path = file_paths[idx]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.file_path, file_paths[idx])

    def test_slug_field(self):
        people = Person.objects.order_by('pk').all()

        slugs = ['jesus', 'buddha', 'clark', 'the-dude', 'donny', 'walter']
        for idx, person in enumerate(people):
            person.slug = slugs[idx]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.slug, slugs[idx])

    def test_text_field(self):
        people = Person.objects.order_by('pk').all()

        texts = ['this is a dummy text', 'dummy text', 'bla bla bla bla bla',
                 'here is a dummy text', 'dummy', 'bla bla bla']
        for idx, person in enumerate(people):
            person.text = texts[idx]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.text, texts[idx])

    def test_url_field(self):
        people = Person.objects.order_by('pk').all()
        urls = ['docs.djangoproject.com', 'news.ycombinator.com',
                'https://docs.djangoproject.com', 'https://google.com',
                'google.com', 'news.ycombinator.com']
        for idx, person in enumerate(people):
            person.url = urls[idx]
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.url, urls[idx])

    def test_date_time_field(self):
        """
            Datetime values are saved correctly
        """

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.date_time = self.now - timedelta(days=1 + idx,
                                                    hours=1 + idx)
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.date_time,
                             self.now - timedelta(days=1 + idx, hours=1 + idx))

    def test_date_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.date = self.date - timedelta(days=1 + idx)
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.date,
                             self.date - timedelta(days=1 + idx))

    def test_time_field(self):
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.time = time(1 + idx, 0 + idx)
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.time, time(1 + idx, 0 + idx))

    def test_decimal_field(self):
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

    def test_float_field(self):
        people = Person.objects.order_by('pk').all()
        initial_values = {p.pk: p.float_height for p in people}
        for idx, person in enumerate(people):
            person.float_height = person.float_height * 2
            initial_values[person.pk] = person.float_height
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.float_height, initial_values[person.pk])

    def test_generic_ipaddress_field(self):
        people = Person.objects.order_by('pk').all()
        remote_addrs = ['127.0.0.1', '192.0.2.30', '2a02:42fe::4']
        values = {}
        for idx, person in enumerate(people):
            remote_addr = random.choice(remote_addrs)
            person.remote_addr = remote_addr
            values[person.pk] = remote_addr
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.remote_addr, values[person.pk])

    def test_file_field(self):
        files = ['dummy.txt', 'kitten.jpg', 'fixtures.json',
                 'dummy.png', 'users.json', 'dummy.png']
        people = Person.objects.order_by('pk').all()
        values = {}
        for idx, person in enumerate(people):
            my_file = random.choice(files)
            person.my_file = my_file
            values[person.pk] = my_file
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.my_file, values[person.pk])

    def test_image_field(self):
        images = ['kitten.jpg', 'dummy.png', 'users.json', 'dummy.png']
        people = Person.objects.order_by('pk').all()
        values = {}
        for idx, person in enumerate(people):
            image = random.choice(images)
            person.image = image
            values[person.pk] = image
        Person.objects.bulk_update(people)

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.image, values[person.pk])

    def test_custom_fields(self):
        values = {}
        people = Person.objects.all()
        people_dict = {p.name: p for p in people}
        person = people_dict['Mike']
        person.data = {'name': 'mikey', 'age': 99, 'ex': -99}
        values[person.pk] = {'name': 'mikey', 'age': 99, 'ex': -99}

        person = people_dict['Mary']
        person.data = {'names': {'name': []}}
        values[person.pk] = {'names': {'name': []}}

        person = people_dict['Pete']
        person.data = []
        values[person.pk] = []

        person = people_dict['Sandra']
        person.data = [{'name': 'Pete'}, {'name': 'Mike'}]
        values[person.pk] = [{'name': 'Pete'}, {'name': 'Mike'}]

        person = people_dict['Ash']
        person.data = {'text': 'bla'}
        values[person.pk] = {'text': 'bla'}

        person = people_dict['Crystal']
        values[person.pk] = person.data

        Person.objects.bulk_update(people)

        people = Person.objects.all()
        for person in people:
            self.assertEqual(person.data, values[person.pk])

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

    def test_object_list(self):
        """
          Pass in a list instead of a queryset for bulk updating
        """
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            person.big_age = idx + 27
        Person.objects.bulk_update(list(people))

        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            self.assertEqual(person.big_age, idx + 27)
