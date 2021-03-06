#!/usr/bin/python
try: import unittest2 as unittest #for Python <= 2.6
except: import unittest
import sys
import pexpect
import subprocess
from selenium import webdriver
from settings_for_fts import INSTALLED_APPS


def start_selenium_server():
    print 'Starting Selenium'
    selenium_server = pexpect.spawn(
        'java',
        args=['-jar', 'selenium-server-standalone-2.8.0.jar']
    )
    try:
        selenium_server.expect(
            'Started org.openqa.jetty.jetty.Server'
        )
    except pexpect.TIMEOUT:
        print 'timeout waiting for selenium to start... try again?'
        sys.exit()
    print 'selenium started'
    return selenium_server


def start_django_server():
    print 'running syncdb'
    subprocess.Popen(
            ['python', 'manage.py', 'syncdb', '--noinput', '--settings=settings_for_fts']
    ).communicate()

    print 'starting django test server'
    #noreload ensures single process
    django_server = subprocess.Popen(
            ['python', 'manage.py', 'runserver', '--noreload', '--settings=settings_for_fts']
    )
    #dev server starts quickly, no need to check it's running
    print 'django test server started'
    return django_server


def run_all_functional_tests():
    print 'running tests'
    tests = unittest.defaultTestLoader.discover('fts')
    runner = unittest.TextTestRunner()
    runner.run(tests)


if __name__ == '__main__':
    selenium = start_selenium_server()
    django = start_django_server()
    run_all_functional_tests()
    selenium.terminate()
    django.kill()


ROOT = 'http://127.0.0.1:8000'

class FunctionalTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)
        self._reset_database()

    def tearDown(self):
        self.browser.close()

    def _reset_database(self):
        my_apps = [app for app in INSTALLED_APPS if '.' not in app]
        for app in my_apps:
            subprocess.Popen(
                ['python', 'manage.py', 'reset', app, '--noinput', '--settings=settings_for_fts']
            ).communicate()



