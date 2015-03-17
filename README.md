django-bulk-update
==================================
[![Build Status](https://travis-ci.org/aykut/django-bulk-update.svg?branch=master)](https://travis-ci.org/aykut/django-bulk-update)
[![Coverage Status](https://coveralls.io/repos/aykut/django-bulk-update/badge.svg?branch=master)](https://coveralls.io/r/aykut/django-bulk-update?branch=master)

Simple bulk update over Django ORM or with helper function.

This project aims to bulk update given objects using **one query** over **Django ORM**.

Installation
==================================
    pip install django-bulk-update

Usage
==================================
With manager:

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


With helper:

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

Performance Tests:
==================================

    setup='''
    from test.person.models import Person
    ids=list(Person.objects.values_list('id', flat=True)[:1000])
    from django.db.models import F
    people=Person.objects.filter(id__in=ids)
    dj_update = lambda: people.update(name=F('name'), surname=F('surname'))
    '''
    >> import timeit
    >> print min(timeit.Timer('dj_update()', setup=setup).repeat(7, 100))
    >> 1.43143701553
    
    setup='''
    from bulk_update import helper
    from test.person.models import Person
    ids=list(Person.objects.values_list('id', flat=True)[:1000])
    people=Person.objects.filter(id__in=ids)
    bu_update = lambda: helper.bulk_update(people, update_fields=['name', 'surname'])
    '''
    
    >> import timeit
    >> print min(timeit.Timer('bu_update()', setup=setup).repeat(7, 100))
    >> 15.0784111023
    
    setup='''
    from test.person.models import Person
    from django.db.models import F
    ids=list(Person.objects.values_list('id', flat=True)[:1000])
    people=Person.objects.filter(id__in=ids)
    def dmmy_update():
        for p in people:
            p.name = F('name')
            p.surname = F('surname')
            p.save(update_fields=['name', 'surname'])
    '''
    
    >> import timeit
    >> print min(timeit.Timer('dmmy_update()', setup=setup).repeat(7, 100))
    >> 201.827591181

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

TODO
==================================
- Tests for every types of model fields, even for a few custom fields.
- Geometry Fields support
