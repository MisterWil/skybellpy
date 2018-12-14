"""
Test Skybell system functionality.

Tests the system initialization and attributes of the main Skybell class.
"""
import os
import json
import unittest

import requests
import requests_mock

import skybellpy
import skybellpy.helpers.constants as CONST

import tests.mock as MOCK
import tests.mock.login as LOGIN
import tests.mock.device as DEVICE
import tests.mock.device_avatar as DEVICE_AVATAR
import tests.mock.device_info as DEVICE_INFO
import tests.mock.device_settings as DEVICE_SETTINGS
import tests.mock.device_activities as DEVICE_ACTIVITIES

USERNAME = 'foobar'
PASSWORD = 'deadbeef'


class TestSkybell(unittest.TestCase):
    """Test the Skybell class in skybellpy."""

    def setUp(self):
        """Set up Skybell module."""
        self.skybell_no_cred = skybellpy.Skybell()
        self.skybell = skybellpy.Skybell(username=USERNAME,
                                         password=PASSWORD,
                                         disable_cache=True)

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
                                    disable_cache=True)

        # pylint: disable=W0212
        self.assertEqual(skybell._username, 'fizz')
        self.assertEqual(skybell._password, 'buzz')
        self.assertEqual(skybell._cache['access_token'], MOCK.ACCESS_TOKEN)
        self.assertIsNone(skybell._devices)

        skybell.logout()

        skybell = None

    @requests_mock.mock()
    def tests_auto_fetch(self, m):
        """Test that automatic device retrieval works."""
        access_token = MOCK.ACCESS_TOKEN
        login_json = LOGIN.post_response_ok(access_token)

        m.post(CONST.LOGIN_URL, text=login_json)
        m.get(CONST.DEVICES_URL, text=DEVICE.EMPTY_DEVICE_RESPONSE)

        skybell = skybellpy.Skybell(username='fizz',
                                    password='buzz',
                                    get_devices=True,
                                    disable_cache=True)

        # pylint: disable=W0212
        self.assertEqual(skybell._username, 'fizz')
        self.assertEqual(skybell._password, 'buzz')
        self.assertEqual(skybell._cache['access_token'], MOCK.ACCESS_TOKEN)
        self.assertEqual(len(skybell._devices), 0)

        skybell.logout()

        skybell = None

    @requests_mock.mock()
    def tests_login_failure(self, m):
        """Test login failed."""
        m.post(CONST.LOGIN_URL,
               text="invalid_client", status_code=400)

        with self.assertRaises(skybellpy.SkybellAuthenticationException):
            self.skybell_no_cred.login(username=USERNAME, password=PASSWORD)

    @requests_mock.mock()
    def tests_full_setup(self, m):
        """Test that Skybell is set up propertly."""
        access_token = MOCK.ACCESS_TOKEN
        login_json = LOGIN.post_response_ok(access_token=access_token)

        m.post(CONST.LOGIN_URL, text=login_json)
        m.get(CONST.DEVICES_URL, text=DEVICE.EMPTY_DEVICE_RESPONSE)

        self.skybell.get_devices()

        # pylint: disable=protected-access
        original_session = self.skybell._session

        # pylint: disable=W0212
        self.assertEqual(self.skybell._username, USERNAME)
        self.assertEqual(self.skybell._password, PASSWORD)
        self.assertEqual(self.skybell._cache['access_token'],
                         MOCK.ACCESS_TOKEN)
        self.assertEqual(len(self.skybell._devices), 0)
        self.assertIsNotNone(self.skybell._session)
        self.assertEqual(self.skybell._session, original_session)

        self.skybell.logout()

        self.assertIsNone(self.skybell._cache['access_token'])
        self.assertIsNone(self.skybell._devices)
        self.assertIsNotNone(self.skybell._session)
        self.assertNotEqual(self.skybell._session, original_session)

        self.skybell.logout()

    @requests_mock.mock()
    def tests_reauthorize(self, m):
        """Check that Skybell can reauthorize after token timeout."""
        new_token = "FOOBAR"
        m.post(CONST.LOGIN_URL, [
            {'text': LOGIN.post_response_ok(
                access_token=new_token), 'status_code': 200}
        ])

        m.get(CONST.DEVICES_URL, [
            {'text': MOCK.UNAUTORIZED, 'status_code': 401},
            {'text': DEVICE.EMPTY_DEVICE_RESPONSE, 'status_code': 200}
        ])

        # Forces a device update
        self.skybell.get_devices(refresh=True)

        # pylint: disable=W0212
        self.assertEqual(self.skybell._cache['access_token'], new_token)

        self.skybell.logout()

    @requests_mock.mock()
    def tests_send_request_exception(self, m):
        """Check that send_request recovers from an exception."""
        new_token = "DEADBEEF"
        m.post(CONST.LOGIN_URL, [
            {'text': LOGIN.post_response_ok(
                access_token=new_token), 'status_code': 200}
        ])

        m.get(CONST.DEVICES_URL, [
            {'exc': requests.exceptions.ConnectTimeout},
            {'text': DEVICE.EMPTY_DEVICE_RESPONSE, 'status_code': 200}
        ])

        # Forces a device update
        self.skybell.get_devices(refresh=True)

        # pylint: disable=W0212
        self.assertEqual(self.skybell._cache['access_token'], new_token)

        self.skybell.logout()

    @requests_mock.mock()
    def tests_continuous_bad_auth(self, m):
        """Check that Skybell won't get stuck with repeated failed retries."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())
        m.get(CONST.DEVICES_URL, text=MOCK.UNAUTORIZED, status_code=401)

        with self.assertRaises(skybellpy.SkybellException):
            self.skybell.get_devices(refresh=True)

        self.skybell.logout()

    @requests_mock.mock()
    def tests_cookies(self, m):
        """Check that cookies are saved and loaded successfully."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Define test pickle file and cleanup old one if exists
        cache_path = "./test_cookies.pickle"

        if os.path.exists(cache_path):
            os.remove(cache_path)

        # Assert that no cookies file exists
        self.assertFalse(os.path.exists(cache_path))

        # Cookies are created
        skybell = skybellpy.Skybell(username='fizz',
                                    password='buzz',
                                    auto_login=False,
                                    cache_path=cache_path)

        # Test that our cookies are fully realized prior to login
        # pylint: disable=W0212
        self.assertIsNotNone(skybell._cache['app_id'])
        self.assertIsNotNone(skybell._cache['client_id'])
        self.assertIsNotNone(skybell._cache['token'])
        self.assertIsNone(skybell._cache['access_token'])

        # Login to get the access_token
        skybell.login()

        # Test that we now have an access token
        self.assertIsNotNone(skybell._cache['access_token'])

        # Test that we now have a cookies file
        self.assertTrue(os.path.exists(cache_path))

        # Copy our current cookies file and data
        first_pickle = open(cache_path, 'rb').read()
        first_cookies_data = skybell._cache

        # Test that logout clears the auth token
        skybell.logout()

        self.assertIsNone(skybell._cache['access_token'])

        # Tests that our pickle file has changed with the cleared token
        self.assertNotEqual(first_pickle, open(cache_path, 'rb').read())

        # New skybell instance reads in old data
        skybell = skybellpy.Skybell(username='fizz',
                                    password='buzz',
                                    auto_login=False,
                                    cache_path=cache_path)

        # Test that the cookie data is the same
        self.assertEqual(skybell._cache['app_id'],
                         first_cookies_data['app_id'])
        self.assertEqual(skybell._cache['client_id'],
                         first_cookies_data['client_id'])
        self.assertEqual(skybell._cache['token'],
                         first_cookies_data['token'])

        # Cleanup cookies
        os.remove(cache_path)

    @requests_mock.mock()
    def test_get_device(self, m):
        """Check that device retrieval works."""
        dev1_devid = 'dev1'
        dev1 = DEVICE.get_response_ok(name='Dev1', dev_id=dev1_devid)
        dev1_avatar = DEVICE_AVATAR.get_response_ok('dev1')
        dev1_avatar_url = str.replace(CONST.DEVICE_AVATAR_URL,
                                      '$DEVID$', dev1_devid)
        dev1_info = DEVICE_INFO.get_response_ok(dev_id=dev1_devid)
        dev1_info_url = str.replace(CONST.DEVICE_INFO_URL,
                                    '$DEVID$', dev1_devid)
        dev1_settings = DEVICE_SETTINGS.get_response_ok()
        dev1_settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                        '$DEVID$', dev1_devid)
        dev1_activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                          '$DEVID$', dev1_devid)

        dev2_devid = 'dev2'
        dev2 = DEVICE.get_response_ok(name='Dev2', dev_id=dev2_devid)
        dev2_avatar = DEVICE_AVATAR.get_response_ok('dev2')
        dev2_avatar_url = str.replace(CONST.DEVICE_AVATAR_URL,
                                      '$DEVID$', dev2_devid)
        dev2_info = DEVICE_INFO.get_response_ok(dev_id=dev1_devid)
        dev2_info_url = str.replace(CONST.DEVICE_INFO_URL,
                                    '$DEVID$', dev2_devid)
        dev2_settings = DEVICE_SETTINGS.get_response_ok()
        dev2_settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                        '$DEVID$', dev2_devid)
        dev2_activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                          '$DEVID$', dev2_devid)

        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())
        m.get(CONST.DEVICES_URL, text='[' + dev1 + ',' + dev2 + ']')
        m.get(dev1_avatar_url, text=dev1_avatar)
        m.get(dev2_avatar_url, text=dev2_avatar)
        m.get(dev1_info_url, text=dev1_info)
        m.get(dev2_info_url, text=dev2_info)
        m.get(dev1_settings_url, text=dev1_settings)
        m.get(dev2_settings_url, text=dev2_settings)
        m.get(dev1_activities_url,
              text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)
        m.get(dev2_activities_url,
              text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)

        # Reset
        self.skybell.logout()

        # Get and test all devices
        # pylint: disable=W0212
        dev1_dev = self.skybell.get_device(dev1_devid)
        dev2_dev = self.skybell.get_device(dev2_devid)

        self.assertIsNotNone(dev1_dev)
        self.assertIsNotNone(dev2_dev)
        self.assertEqual(json.loads(dev1), dev1_dev._device_json)
        self.assertEqual(json.loads(dev2), dev2_dev._device_json)
        self.assertEqual(json.loads(dev1_avatar), dev1_dev._avatar_json)
        self.assertEqual(json.loads(dev2_avatar), dev2_dev._avatar_json)
        self.assertEqual(json.loads(dev1_info), dev1_dev._info_json)
        self.assertEqual(json.loads(dev2_info), dev2_dev._info_json)
        self.assertEqual(json.loads(dev1_settings),
                         dev1_dev._settings_json)
        self.assertEqual(json.loads(dev2_settings),
                         dev2_dev._settings_json)

    @requests_mock.mock()
    def test_all_device_refresh(self, m):
        """Check that device refresh works and reuses the same objects."""
        dev1_devid = 'dev1'
        dev1a = DEVICE.get_response_ok(name='Dev1', dev_id=dev1_devid)
        dev1a_avatar = DEVICE_AVATAR.get_response_ok('dev1a')
        dev1a_avatar_url = str.replace(CONST.DEVICE_AVATAR_URL,
                                       '$DEVID$', dev1_devid)
        dev1a_info = DEVICE_INFO.get_response_ok(dev_id=dev1_devid)
        dev1a_info_url = str.replace(CONST.DEVICE_INFO_URL,
                                     '$DEVID$', dev1_devid)
        dev1a_settings = DEVICE_SETTINGS.get_response_ok()
        dev1a_settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                         '$DEVID$', dev1_devid)

        dev1a_activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                           '$DEVID$', dev1_devid)

        dev2_devid = 'dev2'
        dev2a = DEVICE.get_response_ok(name='Dev2', dev_id=dev2_devid)
        dev2a_avatar = DEVICE_AVATAR.get_response_ok('dev2a')
        dev2a_avatar_url = str.replace(CONST.DEVICE_AVATAR_URL,
                                       '$DEVID$', dev2_devid)
        dev2a_info = DEVICE_INFO.get_response_ok(dev_id=dev1_devid)
        dev2a_info_url = str.replace(CONST.DEVICE_INFO_URL,
                                     '$DEVID$', dev2_devid)
        dev2a_settings = DEVICE_SETTINGS.get_response_ok()
        dev2a_settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                         '$DEVID$', dev2_devid)

        dev2a_activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                           '$DEVID$', dev2_devid)

        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())
        m.get(CONST.DEVICES_URL, text='[' + dev1a + ',' + dev2a + ']')
        m.get(dev1a_avatar_url, text=dev1a_avatar)
        m.get(dev2a_avatar_url, text=dev2a_avatar)
        m.get(dev1a_info_url, text=dev1a_info)
        m.get(dev2a_info_url, text=dev2a_info)
        m.get(dev1a_settings_url, text=dev1a_settings)
        m.get(dev2a_settings_url, text=dev2a_settings)
        m.get(dev1a_activities_url,
              text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)
        m.get(dev2a_activities_url,
              text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)

        # Reset
        self.skybell.logout()

        # Get all devices
        self.skybell.get_devices()

        # Get and check devices
        # pylint: disable=W0212
        dev1a_dev = self.skybell.get_device(dev1_devid)
        self.assertEqual(json.loads(dev1a)['id'], dev1a_dev.device_id)

        dev2a_dev = self.skybell.get_device(dev2_devid)
        self.assertEqual(json.loads(dev2a)['id'], dev2a_dev.device_id)

        # Change device states
        dev1b = DEVICE.get_response_ok(name='Dev1_new', dev_id=dev1_devid)
        dev2b = DEVICE.get_response_ok(name='Dev2_new', dev_id=dev2_devid)

        m.get(CONST.DEVICES_URL, text='[' + dev1b + ',' + dev2b + ']')

        # Refresh all devices
        self.skybell.get_devices(refresh=True)

        # Get and check devices again, ensuring they are the same object
        # Future note: "if a is b" tests that the object is the same
        # Asserting dev1a_dev is dev1b_dev tests if they are the same object
        dev1b_dev = self.skybell.get_device(dev1_devid)
        self.assertEqual(json.loads(dev1b)['id'], dev1b_dev.device_id)
        self.assertIs(dev1a_dev, dev1b_dev)

        dev2b_dev = self.skybell.get_device(dev2_devid)
        self.assertEqual(json.loads(dev2b)['id'], dev2b_dev.device_id)
        self.assertIs(dev2a_dev, dev2b_dev)
