django-bulk-update
==================================
[![Build Status](https://travis-ci.org/aykut/django-bulk-update.svg?branch=master)](https://travis-ci.org/aykut/django-bulk-update)
[![Coverage Status](https://coveralls.io/repos/aykut/django-bulk-update/badge.svg?branch=master)](https://coveralls.io/r/aykut/django-bulk-update?branch=master)

Simple bulk update over Django ORM or with helper function.

This project aims to bulk update given objects using **one query** over
**Django ORM**.

Installation
==================================
    pip install django-bulk-update

Usage
==================================
With manager:

```python
from bulk_update.manager import BulkUpdateManager

class Person(models.Model):
    ...
    objects = BulkUpdateManager()

random_names = ['Walter', 'The Dude', 'Donny', 'Jesus']
people = Person.objects.all()
for person in people:
  r = random.randrange(4)
  person.name = random_names[r]

Person.objects.bulk_update(people, update_fields=['name'])  # updates only name column
Person.objects.bulk_update(people, exclude_fields=['username'])  # updates all columns except username
Person.objects.bulk_update(people)  # updates all columns
Person.objects.bulk_update(people, batch_size=50000)  # updates all columns by 50000 sized chunks
```


With helper:

```python
from bulk_update.helper import bulk_update

random_names = ['Walter', 'The Dude', 'Donny', 'Jesus']
people = Person.objects.all()
for person in people:
  r = random.randrange(4)
  person.name = random_names[r]

bulk_update(people, update_fields=['name'])  # updates only name column
bulk_update(people, exclude_fields=['username'])  # updates all columns except username
bulk_update(people, using='someotherdb')  # updates all columns using the given db
bulk_update(people)  # updates all columns using the default db
bulk_update(people, batch_size=50000)  # updates all columns by 50000 sized chunks using the default db
```

Performance Tests:
==================================

```python
# Note: SQlite is unable to run the `timeit` tests
# due to the max number of sql variables
In [1]: import os
In [2]: import timeit
In [3]: import django

In [4]: os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
In [5]: django.setup()

In [6]: from tests.fixtures import create_fixtures

In [7]: django.db.connection.creation.create_test_db()
In [8]: create_fixtures(1000)

In [9]: setup='''
  ....: from tests.models import Person
  ....: ids=list(Person.objects.values_list('id', flat=True)[:1000])
  ....: from django.db.models import F
  ....: people=Person.objects.filter(id__in=ids)
  ....: dj_update = lambda: people.update(name=F('name'), email=F('email'))
  ....: '''
In [10]: print "Django update performance:", min(timeit.Timer('dj_update()', setup=setup).repeat(7, 100))
Django update performance: 1.1035900116

In [11]: setup='''
  ....: from bulk_update import helper
  ....: from tests.models import Person
  ....: ids=list(Person.objects.values_list('id', flat=True)[:1000])
  ....: people=Person.objects.filter(id__in=ids)
  ....: bu_update = lambda: helper.bulk_update(people, update_fields=['name', 'email'])
  ....: '''
In [12]: print "Bulk update performance:", min(timeit.Timer('bu_update()', setup=setup).repeat(7, 100))
Bulk update performance: 11.0196619034

In [13]: setup='''
  ....: from tests.models import Person
  ....: from django.db.models import F
  ....: ids=list(Person.objects.values_list('id', flat=True)[:1000])
  ....: people=Person.objects.filter(id__in=ids)
  ....: def dmmy_update():
  ....:     for p in people:
  ....:         p.name = F('name')
  ....:         p.email = F('email')
  ....:         p.save(update_fields=['name', 'email'])
  ....: '''
In [14]: print "Naive update performance", min(timeit.Timer('dmmy_update()', setup=setup).repeat(7, 100))
Naive update performance 340.86224699
```

Requirements
==================================
- Django 1.2+

Contributors
==================================
- [aykut](https://github.com/aykut)
- [daleobrien](https://github.com/daleobrien)
- [sruon](https://github.com/sruon)
- [HowerHell](https://github.com/HoverHell)
- [c-nichols](https://github.com/c-nichols)
- [towr](https://github.com/towr)
- [joshblum](https://github.com/joshblum)

TODO
==================================
- Geometry Fields support
