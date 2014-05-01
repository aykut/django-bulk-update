django-bulk-update
==================================

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

Requirements
==================================
- Django 1.2+

TODO
==================================
- UnitTests
- Performance Tests
