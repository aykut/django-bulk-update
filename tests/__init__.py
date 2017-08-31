from datetime import time, date, timedelta
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase


class BulkAndCreateCommon(object):

    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)  # mysql doesn't do microseconds. # NOQA
        self.date = date(2015, 3, 28)
        self.time = time(13, 0)

    def _test_field(self, field, idx_to_value_function):
        raise NotImplementedError('Implement it in the concrete class')

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

    def test_data_field(self):
        fn = lambda idx: {'x': idx}
        self._test_field('data',  fn)

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
