"""
Test Skybell system functionality.

Tests the system initialization and attributes of the main Skybell class.
"""
import json
import unittest

import requests
import requests_mock

import skybellpy
import skybellpy.helpers.constants as CONST

import tests.mock as MOCK
import tests.mock.login as LOGIN

USERNAME = 'foobar'
PASSWORD = 'deadbeef'


class TestSkybell(unittest.TestCase):
    """Test the Skybell class in skybellpy."""

    def setUp(self):
        """Set up Skybell module."""
        self.skybell_no_cred = skybellpy.Skybell()
        self.skybell = skybellpy.Skybell(username=USERNAME,
                                   password=PASSWORD)

    def tearDown(self):
        """Clean up after test."""
        self.skybell = None
        self.skybell_no_cred = None

    def tests_initialization(self):
        """Verify we can initialize skybell."""
        # pylint: disable=protected-access
        self.assertEqual(self.skybell._username, USERNAME)
        # pylint: disable=protected-access
        self.assertEqual(self.skybell._password, PASSWORD)

    def tests_no_credentials(self):
        """Check that we throw an exception when no username/password."""
        with self.assertRaises(skybellpy.SkybellAuthenticationException):
            self.skybell_no_cred.login()

        # pylint: disable=protected-access
        self.skybell_no_cred._username = USERNAME
        with self.assertRaises(skybellpy.SkybellAuthenticationException):
            self.skybell_no_cred.login()

    @requests_mock.mock()
    def tests_manual_login(self, m):
        """Check that we can manually use the login() function."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        self.skybell_no_cred.login(username=USERNAME, password=PASSWORD)

        # pylint: disable=protected-access
        self.assertEqual(self.skybell_no_cred._username, USERNAME)
        # pylint: disable=protected-access
        self.assertEqual(self.skybell_no_cred._password, PASSWORD)

    @requests_mock.mock()
    def tests_auto_login(self, m):
        """Test that automatic login works."""
        access_token = MOCK.ACCESS_TOKEN
        login_json = LOGIN.post_response_ok(access_token)

        m.post(CONST.LOGIN_URL, text=login_json)

        skybell = skybellpy.Skybell(username='fizz',
                                    password='buzz',
                                    auto_login=True,
                                    get_devices=False,
                                    disable_cookies=True)

        # pylint: disable=W0212
        self.assertEqual(skybell._username, 'fizz')
        self.assertEqual(skybell._password, 'buzz')
        self.assertEqual(skybell._cookies['access_token'], MOCK.ACCESS_TOKEN)
        self.assertIsNone(skybell._devices)

        skybell.logout()

        skybell = None
