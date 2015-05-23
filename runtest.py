#!/usr/bin/env python
import os
import sys
import django

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    from django.conf import settings
    from django.test.utils import get_runner

    if django.VERSION >= (1, 7):
       django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
