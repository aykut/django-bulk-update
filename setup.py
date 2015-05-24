import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bulk-update',
    version='1.1.3',
    packages=find_packages(),
    include_package_data=True,
    description='Bulk update using one query over Django ORM.',
    long_description=README,
    url='https://github.com/aykut/django-bulk-update',
    author='Aykut Ozat',
    author_email='aykutozat@gmail.com',
    install_requires=[
        'django>=1.2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
