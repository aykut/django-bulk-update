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

    def _test_field(self, field, idx_to_value_function):
        '''
        Helper to do repeative simple tests on one field.
        '''

        # set
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            value = idx_to_value_function(idx)
            setattr(person, field, value)

        # update
        Person.objects.bulk_update(people, update_fields=[field])

        # check
        people = Person.objects.order_by('pk').all()
        for idx, person in enumerate(people):
            saved_value = getattr(person, field)
            expected_value = idx_to_value_function(idx)
            self.assertEqual(saved_value, expected_value)

    def test_simple_fields(self):
        fn = lambda idx: idx + 27
        for field in ('default', 'big_age', 'age', 'positive_age',
                      'positive_small_age', 'small_age'):
            self._test_field(field,  fn)

    def test_comma_separated_integer_field(self):
        fn = lambda idx: str(idx) + ',27'
        self._test_field('comma_separated_age',  fn)

    def test_boolean_field(self):
        fn = lambda idx: [True, False][idx % 2]
        self._test_field('certified',  fn)

    def test_null_boolean_field(self):
        fn = lambda idx: [True, False, None][idx % 3]
        self._test_field('null_certified',  fn)

    def test_char_field(self):
        NAMES = ['Walter', 'The Dude', 'Donny', 'Jesus', 'Buddha', 'Clark']
        fn = lambda idx: NAMES[idx % 5]
        self._test_field('name',  fn)

    def test_email_field(self):
        EMAILS = ['walter@mailinator.com', 'thedude@mailinator.com',
                  'donny@mailinator.com', 'jesus@mailinator.com',
                  'buddha@mailinator.com', 'clark@mailinator.com']
        fn = lambda idx: EMAILS[idx % 5]
        self._test_field('email',  fn)

    def test_file_path_field(self):
        PATHS = ['/home/dummy.txt', '/Downloads/kitten.jpg',
                 '/Users/user/fixtures.json', 'dummy.png',
                 'users.json', '/home/dummy.png']
        fn = lambda idx: PATHS[idx % 5]
        self._test_field('file_path',  fn)

    def test_slug_field(self):
        SLUGS = ['jesus', 'buddha', 'clark', 'the-dude', 'donny', 'walter']
        fn = lambda idx: SLUGS[idx % 5]
        self._test_field('slug',  fn)

    def test_text_field(self):
        TEXTS = ['this is a dummy text', 'dummy text', 'bla bla bla bla bla',
                 'here is a dummy text', 'dummy', 'bla bla bla']
        fn = lambda idx: TEXTS[idx % 5]
        self._test_field('text',  fn)

    def test_url_field(self):
        URLS = ['docs.djangoproject.com', 'news.ycombinator.com',
                'https://docs.djangoproject.com', 'https://google.com',
                'google.com', 'news.ycombinator.com']
        fn = lambda idx: URLS[idx % 5]
        self._test_field('url',  fn)

    def test_date_time_field(self):
        fn = lambda idx: self.now - timedelta(days=1 + idx, hours=1 + idx)
        self._test_field('date_time',  fn)

    def test_date_field(self):
        fn = lambda idx: self.date - timedelta(days=1 + idx)
        self._test_field('date',  fn)

    def test_time_field(self):
        fn = lambda idx: time(1 + idx, idx)
        self._test_field('time',  fn)

    def test_decimal_field(self):
        fn = lambda idx: Decimal('1.%s' % (50 + idx * 7))
        self._test_field('height',  fn)

    def test_float_field(self):
        fn = lambda idx: float(idx) * 2.0
        self._test_field('float_height',  fn)

    def test_generic_ipaddress_field(self):
        IPS = ['127.0.0.1', '192.0.2.30', '2a02:42fe::4', '10.0.0.1',
               '8.8.8.8']
        fn = lambda idx: IPS[idx % 5]
        self._test_field('remote_addr',  fn)

    def test_image_field(self):
        IMGS = ['kitten.jpg', 'dummy.png', 'user.json', 'dummy.png', 'foo.gif']
        fn = lambda idx: IMGS[idx % 5]

        self._test_field('image',  fn)
        self._test_field('my_file',  fn)

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

    def test_empty_list(self):
        """
        Update no elements, passed as a list
        """
        Person.objects.bulk_update([])

    def test_empty_queryset(self):
        """
        Update no elements, passed as a queryset
        """
        Person.objects.bulk_update(Person.objects.filter(name="Aceldotanrilsteucsebces ECSbd (funny name, isn't it?)"))

