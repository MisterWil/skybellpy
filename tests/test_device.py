"""
Test Skybell device functionality.

Tests the device initialization and attributes of the Skybell device class.
"""
import datetime
import json
import unittest

from distutils import utils as ut

import requests_mock

import skybellpy
import skybellpy.helpers.constants as CONST

import tests.mock.login as LOGIN
import tests.mock.device as DEVICE
import tests.mock.device_info as DEVICE_INFO
import tests.mock.device_settings as DEVICE_SETTINGS
import tests.mock.device_activities as DEVICE_ACTIVITIES

USERNAME = 'foobar'
PASSWORD = 'deadbeef'


class TestSkybell(unittest.TestCase):
    """Test the Skybell class in skybellpy."""

    def setUp(self):
        """Set up Skybell module."""
        self.skybell = skybellpy.Skybell(username=USERNAME,
                                         password=PASSWORD,
                                         disable_cache=True)

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

        info_text = DEVICE_INFO.get_response_ok()
        info_json = json.loads(info_text)
        info_url = str.replace(CONST.DEVICE_INFO_URL,
                               '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_json = json.loads(settings_text)
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)

        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)

        # Check device states match
        self.assertIsNotNone(device)
        # pylint: disable=W0212

        # Test Device Details
        self.assertEqual(device.name, device_json[0][CONST.NAME])
        self.assertEqual(device.type, device_json[0][CONST.TYPE])
        self.assertEqual(device.status, device_json[0][CONST.STATUS])
        self.assertEqual(device.device_id, device_json[0][CONST.ID])
        self.assertTrue(device.is_up)
        self.assertEqual(device.location[0],
                         device_json[0][CONST.LOCATION][CONST.LOCATION_LAT])
        self.assertEqual(device.location[1],
                         device_json[0][CONST.LOCATION][CONST.LOCATION_LNG])
        self.assertEqual(device.image,
                         device_json[0][CONST.AVATAR][CONST.AVATAR_URL])

        # Test Info Details
        self.assertEqual(device.wifi_status,
                         info_json[CONST.STATUS][CONST.WIFI_LINK])
        self.assertEqual(device.wifi_ssid, info_json[CONST.WIFI_SSID])
        self.assertEqual(device.last_check_in,
                         info_json[CONST.CHECK_IN])

        # Test Settings Details
        self.assertEqual(device.do_not_disturb,
                         settings_json[CONST.SETTINGS_DO_NOT_DISTURB])
        self.assertEqual(device.outdoor_chime_level,
                         settings_json[CONST.SETTINGS_OUTDOOR_CHIME])
        self.assertEqual(device.motion_sensor,
                         (settings_json[CONST.SETTINGS_MOTION_POLICY] ==
                          CONST.SETTINGS_MOTION_POLICY_ON))
        self.assertEqual(device.motion_threshold,
                         settings_json[CONST.SETTINGS_MOTION_THRESHOLD])
        self.assertEqual(device.video_profile,
                         settings_json[CONST.SETTINGS_VIDEO_PROFILE])
        self.assertEqual(device.led_rgb,
                         (settings_json[CONST.SETTINGS_LED_R],
                          settings_json[CONST.SETTINGS_LED_G],
                          settings_json[CONST.SETTINGS_LED_B]))
        self.assertEqual(device.led_intensity,
                         settings_json[CONST.SETTINGS_LED_INTENSITY])
        # Test Desc
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
        info_text = DEVICE_INFO.get_response_ok(
            ssid=device_ssid, wifi_status=device_wifi_status)
        info_url = str.replace(CONST.DEVICE_INFO_URL,
                               '$DEVID$', DEVICE.DEVID)

        do_not_disturb = False
        outdoor_chime = CONST.SETTINGS_OUTDOOR_CHIME_HIGH
        motion_policy = CONST.SETTINGS_MOTION_POLICY_ON
        motion_threshold = CONST.SETTINGS_MOTION_THRESHOLD_HIGH
        video_profile = CONST.SETTINGS_VIDEO_PROFILE_720P_BETTER
        led_rgb = (255, 255, 255)
        led_intensity = 100
        settings_text = DEVICE_SETTINGS.get_response_ok(
            do_not_disturb,
            outdoor_chime,
            motion_policy,
            motion_threshold,
            video_profile,
            led_rgb,
            led_intensity)
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)
        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)

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
        self.assertEqual(device.do_not_disturb, do_not_disturb)
        self.assertEqual(device.outdoor_chime_level, outdoor_chime)
        self.assertTrue(device.outdoor_chime)
        self.assertEqual(device.motion_sensor, True)
        self.assertEqual(device.motion_threshold, motion_threshold)
        self.assertEqual(device.video_profile, video_profile)
        self.assertEqual(device.led_rgb, led_rgb)
        self.assertEqual(device.led_intensity, led_intensity)

        # Change the values
        device_name = 'Shut The Front Door'
        device_text = DEVICE.get_response_ok(name=device_name)
        device_url = str.replace(CONST.DEVICE_URL, '$DEVID$', DEVICE.DEVID)

        device_ssid = 'Gamecube'
        device_wifi_status = 'bad'
        info_text = DEVICE_INFO.get_response_ok(
            ssid=device_ssid, wifi_status=device_wifi_status)

        do_not_disturb = True
        outdoor_chime = CONST.SETTINGS_OUTDOOR_CHIME_OFF
        motion_policy = CONST.SETTINGS_MOTION_POLICY_OFF
        motion_threshold = CONST.SETTINGS_MOTION_THRESHOLD_LOW
        video_profile = CONST.SETTINGS_VIDEO_PROFILE_480P
        led_rgb = (128, 128, 128)
        led_intensity = 25
        settings_text = DEVICE_SETTINGS.get_response_ok(
            do_not_disturb,
            outdoor_chime,
            motion_policy,
            motion_threshold,
            video_profile,
            led_rgb,
            led_intensity)

        m.get(device_url, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)

        # Refresh the device
        device = self.skybell.get_device(DEVICE.DEVID, refresh=True)

        # Check new values
        self.assertEqual(device.name, device_name)
        self.assertEqual(device.wifi_status, device_wifi_status)
        self.assertEqual(device.wifi_ssid, device_ssid)
        self.assertEqual(device.name, device_name)
        self.assertEqual(device.wifi_status, device_wifi_status)
        self.assertEqual(device.wifi_ssid, device_ssid)
        self.assertEqual(device.do_not_disturb, do_not_disturb)
        self.assertEqual(device.outdoor_chime_level, outdoor_chime)
        self.assertFalse(device.outdoor_chime)
        self.assertEqual(device.motion_sensor, False)
        self.assertEqual(device.motion_threshold, motion_threshold)
        self.assertEqual(device.video_profile, video_profile)
        self.assertEqual(device.led_rgb, led_rgb)
        self.assertEqual(device.led_intensity, led_intensity)

    @requests_mock.mock()
    def tests_settings_change(self, m):
        """Check that the Skybell device changes data."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)
        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)
        m.patch(settings_url, text=DEVICE_SETTINGS.PATCH_RESPONSE_OK)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        # pylint: disable=W0212
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)

        # Change and test new values
        for value in CONST.SETTINGS_DO_NOT_DISTURB_VALUES:
            device.do_not_disturb = value
            self.assertEqual(device.do_not_disturb,
                             distutils.util.strtobool(value))

        for value in CONST.SETTINGS_OUTDOOR_CHIME_VALUES:
            device.outdoor_chime_level = value
            self.assertEqual(device.outdoor_chime_level, value)

        for value in [True, False]:
            device.motion_sensor = value
            self.assertEqual(device.motion_sensor, value)

        for value in CONST.SETTINGS_MOTION_THRESHOLD_VALUES:
            device.motion_threshold = value
            self.assertEqual(device.motion_threshold, value)

        for value in CONST.SETTINGS_VIDEO_PROFILE_VALUES:
            device.video_profile = value
            self.assertEqual(device.video_profile, value)

        for value in CONST.SETTINGS_LED_VALUES:
            rgb = (value, value, value)
            device.led_rgb = rgb
            self.assertEqual(device.led_rgb, rgb)

        for value in CONST.SETTINGS_LED_INTENSITY_VALUES:
            device.led_intensity = value
            self.assertEqual(device.led_intensity, value)

    @requests_mock.mock()
    def tests_settings_validation(self, m):
        """Check that the Skybell device settings validate."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)
        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)
        m.patch(settings_url, text=DEVICE_SETTINGS.PATCH_RESPONSE_OK)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)

        # Change and test new values
        with self.assertRaises(skybellpy.SkybellException):
            device.do_not_disturb = "monkey"

        with self.assertRaises(skybellpy.SkybellException):
            device.outdoor_chime_level = "bamboo"

        with self.assertRaises(skybellpy.SkybellException):
            device.motion_sensor = "dumbo"

        with self.assertRaises(skybellpy.SkybellException):
            device.motion_threshold = "lists"

        with self.assertRaises(skybellpy.SkybellException):
            device.video_profile = "alpha"

        with self.assertRaises(skybellpy.SkybellException):
            device.led_rgb = "grapes"

        with self.assertRaises(skybellpy.SkybellException):
            device.led_rgb = ("oranges", "apples", "peaches")

        with self.assertRaises(skybellpy.SkybellException):
            device.led_rgb = (500, -600, 70.1)

        with self.assertRaises(skybellpy.SkybellException):
            device.led_rgb = (-1, 266, 11)

        with self.assertRaises(skybellpy.SkybellException):
            device.led_intensity = "purple"

        with self.assertRaises(skybellpy.SkybellException):
            device.led_intensity = -500

        with self.assertRaises(skybellpy.SkybellException):
            device.led_intensity = 70.1

        with self.assertRaises(skybellpy.SkybellException):
            # pylint: disable=W0212
            device._set_setting({"lol": "kik"})

        with self.assertRaises(skybellpy.SkybellException):
            # pylint: disable=W0212
            device._set_setting({CONST.SETTINGS_MOTION_POLICY: "kik"})

    @requests_mock.mock()
    def tests_settings_failed(self, m):
        """Check that the Skybell device settings fail without changing."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok(
            do_not_disturb=True)
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)
        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=DEVICE_ACTIVITIES.EMPTY_ACTIVITIES_RESPONSE)
        m.patch(settings_url, text=DEVICE_SETTINGS.PATHCH_RESPONSE_BAD_REQUEST,
                status_code=400)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)
        self.assertEqual(device.do_not_disturb, True)

        # Test setting to false then validate still True
        device.do_not_disturb = False
        self.assertEqual(device.do_not_disturb, True)

    @requests_mock.mock()
    def tests_activities(self, m):
        """Check that the Skybell device activities work."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)

        activities_text = '[' + \
            DEVICE_ACTIVITIES.get_response_ok(
                dev_id=DEVICE.DEVID,
                event=CONST.EVENT_BUTTON) + ',' + \
            DEVICE_ACTIVITIES.get_response_ok(
                dev_id=DEVICE.DEVID,
                event=CONST.EVENT_MOTION) + ',' + \
            DEVICE_ACTIVITIES.get_response_ok(
                dev_id=DEVICE.DEVID,
                event=CONST.EVENT_ON_DEMAND) + ']'
        activities_json = json.loads(activities_text)

        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=activities_text)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)
        # pylint: disable=W0212
        self.assertEqual(device._activities, activities_json)

        # Get all activities from device
        activities = device.activities(limit=100)
        self.assertIsNotNone(activities)
        self.assertEqual(len(activities), 3)

        # Get only button activities
        activities = device.activities(event=CONST.EVENT_BUTTON)
        self.assertIsNotNone(activities)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0][CONST.EVENT], CONST.EVENT_BUTTON)

    @requests_mock.mock()
    def tests_bad_activities(self, m):
        """Check that device activities recovers from bad data."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)

        activities_text = DEVICE_ACTIVITIES.get_response_ok(
            dev_id=DEVICE.DEVID,
            event=CONST.EVENT_BUTTON)

        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=activities_text)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)

        # Get all activities from device
        activities = device.activities(limit=100)
        self.assertIsNotNone(activities)
        self.assertEqual(len(activities), 1)

        # Force our device variable empty
        # pylint: disable=W0212
        device._activities = None

        # Get all activities from device
        activities = device.activities(limit=100)
        self.assertIsNotNone(activities)
        self.assertEqual(len(activities), 0)

    @requests_mock.mock()
    def tests_latest_event(self, m):
        """Check that the latest event is always obtained."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device_text = '[' + DEVICE.get_response_ok() + ']'
        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)

        activity_1 = DEVICE_ACTIVITIES.get_response_ok(
            dev_id=DEVICE.DEVID,
            event=CONST.EVENT_BUTTON,
            state='alpha',
            created_at=datetime.datetime(2017, 1, 1, 0, 0, 0))

        activity_2 = DEVICE_ACTIVITIES.get_response_ok(
            dev_id=DEVICE.DEVID,
            event=CONST.EVENT_BUTTON,
            state='beta',
            created_at=datetime.datetime(2017, 1, 1, 0, 0, 1))

        activities_text = '[' + activity_1 + ',' + activity_2 + ']'

        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text=activities_text)

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)

        # Get latest button event
        event = device.latest(CONST.EVENT_BUTTON)

        # Test
        self.assertIsNotNone(event)
        self.assertEqual(event.get(CONST.STATE), 'beta')

    @requests_mock.mock()
    def tests_newest_event_cached(self, m):
        """Check that the a newer cached event is kept over an older event."""
        m.post(CONST.LOGIN_URL, text=LOGIN.post_response_ok())

        # Set up device
        device = DEVICE.get_response_ok()
        device_text = '[' + device + ']'
        device_url = str.replace(CONST.DEVICE_URL, '$DEVID$', DEVICE.DEVID)

        info_text = DEVICE_INFO.get_response_ok()
        info_url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', DEVICE.DEVID)

        settings_text = DEVICE_SETTINGS.get_response_ok()
        settings_url = str.replace(CONST.DEVICE_SETTINGS_URL,
                                   '$DEVID$', DEVICE.DEVID)

        activity_1 = DEVICE_ACTIVITIES.get_response_ok(
            dev_id=DEVICE.DEVID,
            event=CONST.EVENT_BUTTON,
            state='alpha',
            created_at=datetime.datetime(2017, 1, 1, 0, 0, 0))

        activities_url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                                     '$DEVID$', DEVICE.DEVID)

        m.get(CONST.DEVICES_URL, text=device_text)
        m.get(device_url, text=device)
        m.get(info_url, text=info_text)
        m.get(settings_url, text=settings_text)
        m.get(activities_url, text='[' + activity_1 + ']')

        # Logout to reset everything
        self.skybell.logout()

        # Get our specific device
        device = self.skybell.get_device(DEVICE.DEVID)
        self.assertIsNotNone(device)

        # Get latest button event
        event = device.latest(CONST.EVENT_BUTTON)

        # Test
        self.assertIsNotNone(event)
        self.assertEqual(event.get(CONST.STATE), 'alpha')

        activity_2 = DEVICE_ACTIVITIES.get_response_ok(
            dev_id=DEVICE.DEVID,
            event=CONST.EVENT_BUTTON,
            state='beta',
            created_at=datetime.datetime(2014, 1, 1, 0, 0, 1))

        m.get(activities_url, text='[' + activity_2 + ']')

        # Refresh device
        device.refresh()

        # Get latest button event
        event = device.latest(CONST.EVENT_BUTTON)

        # Test
        self.assertIsNotNone(event)
        self.assertEqual(event.get(CONST.STATE), 'alpha')
