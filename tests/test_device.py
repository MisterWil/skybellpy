"""
Test Skybell device functionality.

Tests the device initialization and attributes of the Skybell device class.
"""
import json
import unittest

import requests_mock

import skybellpy
import skybellpy.helpers.constants as CONST

import tests.mock.login as LOGIN
import tests.mock.device as DEVICE
import tests.mock.device_info as DEVICE_INFO

USERNAME = 'foobar'
PASSWORD = 'deadbeef'


class TestSkybell(unittest.TestCase):
    """Test the Skybell class in skybellpy."""

    def setUp(self):
        """Set up Skybell module."""
        self.skybell = skybellpy.Skybell(username=USERNAME,
                                         password=PASSWORD,
                                         disable_cookies=True)

    def tearDown(self):
        """Clean up after test."""
        self.skybell = None

    @requests_mock.mock()
    def tests_device_init(self, m):
        """Check that the Skybell device init's properly."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        device_json = json.loads(device_text)

        device_info_text = DEVICE_INFO.get_response_ok()
        device_info_json = json.loads(device_info_text)
        device_info_url = CONST.DEVICE_INFO_URL.replace('$DEVID$',
                                                        DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(device_info_url, text=device_info_text)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)

        # Check device states match
        self.assertIsNotNone(device)
        # pylint: disable=W0212
        self.assertEqual(device.name, device_json[0]['name'])
        self.assertEqual(device.type, device_json[0]['type'])
        self.assertEqual(device.status, device_json[0]['status'])
        self.assertEqual(device.device_id, device_json[0]['id'])
        self.assertTrue(device.is_up)
        self.assertEqual(device.location[0], device_json[0]['location']['lat'])
        self.assertEqual(device.location[1], device_json[0]['location']['lng'])
        self.assertEqual(device.image, device_json[0]['avatar']['url'])
        self.assertEqual(device.wifi_status,
                         device_info_json['status']['wifiLink'])
        self.assertEqual(device.wifi_ssid, device_info_json['essid'])
        self.assertEqual(device.last_check_in,
                         device_info_json['checkedInAt'])
        self.assertIsNotNone(device.desc)

    @requests_mock.mock()
    def tests_device_refresh(self, m):
        """Check that the Skybell device refreshes data."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_name = 'Shut The Back Door'
        device_text = '[' + DEVICE.get_response_ok(name=device_name) + ']'

        device_ssid = 'Super SSID64'
        device_wifi_status = 'good'
        device_info_text = DEVICE_INFO.get_response_ok(
            ssid=device_ssid, wifi_status=device_wifi_status)
        device_info_url = CONST.DEVICE_INFO_URL.replace('$DEVID$',
                                                        DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(device_info_url, text=device_info_text)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)

        # Check device states match
        self.assertIsNotNone(device)
        # pylint: disable=W0212
        self.assertEqual(device.name, device_name)
        self.assertEqual(device.wifi_status, device_wifi_status)
        self.assertEqual(device.wifi_ssid, device_ssid)

        # Change the values
        device_name = 'Shut The Front Door'
        device_text = DEVICE.get_response_ok(name=device_name)
        device_url = CONST.DEVICE_URL.replace('$DEVID$', DEVICE.DEVID)

        device_ssid = 'Gamecube'
        device_wifi_status = 'bad'
        device_info_text = DEVICE_INFO.get_response_ok(
            ssid=device_ssid, wifi_status=device_wifi_status)

        m.get(device_url, text=device_text)
        m.get(device_info_url, text=device_info_text)

        # Refresh the device
        device = self.skybell.get_device(DEVICE.DEVID, refresh=True)

        # Check new values
        self.assertEqual(device.name, device_name)
        self.assertEqual(device.wifi_status, device_wifi_status)
        self.assertEqual(device.wifi_ssid, device_ssid)
