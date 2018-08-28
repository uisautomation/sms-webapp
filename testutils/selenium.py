"""
Utilities for interacting with selenium tests.

"""
import atexit
import functools
import unittest
import urllib.parse

from django.conf import settings
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browserstack.local import Local


BROWSER_CAPS = [
    {
        'browser': 'IE',
        'browser_version': '11.0',
        'os': 'Windows',
        'os_version': '7',
    },
    DesiredCapabilities.CHROME,
    DesiredCapabilities.FIREFOX,
]


def with_webdrivers(f):
    """
    Decorator for a test suite or individual tests which passes a web driver instance as the first
    argument. Runs the decorated function once per driver using TestCase.subTest. Will skip the
    test if a selenium command executor is not set.

    To ensure speedy test runs, the drivers are cached and shared between tests. This is non-ideal
    from a test isolation perspective but makes the test suite run far faster.

    Note: this decorator should be within a LiveServerTestCase if it is to have any effect. E.g:

    .. code::

        class MyTestCase(LiveServerTestCase):
            @with_webdrivers
            def test_some_thing(self, driver):
                # ...

    """
    url = getattr(settings, 'TESTUTILS_WEBDRIVER_COMMAND_EXECUTOR', '')

    @unittest.skipIf(url == '', 'TESTUTILS_WEBDRIVER_COMMAND_EXECUTOR is not set')
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        for driver in get_drivers():
            with self.subTest(driver=driver):
                self.driver = driver
                f(self, *args, **kwargs)
    return wrapper


def get_drivers():
    """
    Get a list of webdriver drivers for the application. The return value is cached and so it is
    safe to call this multiple times.

    If the TESTUTILS_WEBDRIVER_BROWSERSTACK_ACCESS_KEY setting is present and non-empty, a
    browerstack local proxy is spun up as well.

    """
    url = getattr(settings, 'TESTUTILS_WEBDRIVER_COMMAND_EXECUTOR', '')
    access_key = getattr(settings, 'TESTUTILS_WEBDRIVER_BROWSERSTACK_ACCESS_KEY', '')
    binary_path = getattr(settings, 'TESTUTILS_WEBDRIVER_BROWSERSTACKLOCAL_PATH', None)

    if access_key != '' and not hasattr(get_drivers, '__cached_local'):
        start_kwargs = {'key': access_key}
        if binary_path is not None:
            start_kwargs['binarypath'] = binary_path
        get_drivers.__cached_local = Local()
        atexit.register(get_drivers.__cached_local.stop)
        get_drivers.__cached_local.start(**start_kwargs)

    if not hasattr(get_drivers, '__cached_drivers'):
        if url == '':
            get_drivers.__cached_drivers = []
        else:
            get_drivers.__cached_drivers = [
                webdriver.Remote(
                    command_executor=url,
                    desired_capabilities={'browserstack.local': True, **cap}
                )
                for cap in BROWSER_CAPS
            ]

        # Make sure to quit the session when we exit
        for driver in get_drivers.__cached_drivers:
            atexit.register(driver.quit)

    return get_drivers.__cached_drivers


class SeleniumTestCase(LiveServerTestCase):
    #host = settings.TESTUTILS_LIVE_SERVER_TEST_CASE_HOST
    host = '0.0.0.0'
    port = 8000

    def setUp(self):
        super().setUp()
        self.driver = None

    def get_absolute_uri(self, url):
        """
        Use urljoin to take a URL which is relative to the site, build an absolute URL suitable for
        passing to the passed webdriver and call driver.get() on it.

        """
        #return self.driver.get(urllib.parse.urljoin(self.live_server_url, url))
        return self.driver.get(urllib.parse.urljoin('http://tox:8000/', url))

    def get_reverse(self, *args, **kwargs):
        """
        Convenience wrapper around reverse which passes the result to :py:funf:`.get_absolute_uri`.

        """
        return self.get_absolute_uri(reverse(*args, **kwargs))
