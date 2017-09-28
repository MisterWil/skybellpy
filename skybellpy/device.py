"""The device class used by SkybellPy."""
import json
import logging

from skybellpy.exceptions import SkybellException
import skybellpy.helpers.constants as CONST
import skybellpy.helpers.errors as ERROR

_LOGGER = logging.getLogger(__name__)


class SkybellDevice(object):
    """Class to represent each Skybell device."""

    def __init__(self, device_json, skybell):
        """Set up Skybell device."""
        self._device_json = device_json
        self._device_id = device_json.get(CONST.ID)
        self._type = device_json.get(CONST.TYPE)
        self._skybell = skybell

        self._device_info_json = self._device_info_request()
        self._device_settings_json = self._device_settings_request()
        self._device_activities = self._device_activities_request()

    def refresh(self):
        """Refresh the devices json object data."""
        new_device_json = self._device_request()
        _LOGGER.debug("Device Refresh Response: %s", new_device_json)

        new_device_info_json = self._device_info_request()
        _LOGGER.debug("Device Info Refresh Response: %s", new_device_info_json)

        new_device_settings_json = self._device_settings_request()
        _LOGGER.debug("Device Settings Refresh Response: %s",
                      new_device_settings_json)

        self.update(new_device_json, new_device_info_json,
                    new_device_settings_json)

        self._device_activities = self._device_activities_request()
        _LOGGER.debug("Device Activities Response: %s",
                      new_device_settings_json)

    def _device_request(self):
        url = str.replace(CONST.DEVICE_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def _device_info_request(self):
        url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def _device_settings_request(self, method="get", json_data=None):
        url = str.replace(CONST.DEVICE_SETTINGS_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method=method,
                                              url=url,
                                              json_data=json_data)
        return json.loads(response.text)

    def _device_activities_request(self):
        url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                          '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def update(self, device_json=None, device_info_json=None,
               device_settings_json=None):
        """Update the json data from a dictionary.

        Only updates if it already exists in the device.
        """
        if device_json:
            self._device_json.update(
                {k: device_json[k] for k in device_json
                 if k in self._device_json})

        if device_info_json:
            self._device_info_json.update(
                {k: device_info_json[k] for k in device_info_json
                 if k in self._device_info_json})

        if device_settings_json:
            self._device_settings_json.update(
                {k: device_settings_json[k] for k in device_settings_json
                 if k in self._device_settings_json})

    def _set_setting(self, settings):
        """Validate the settings and then send the PATCH request."""
        for key, value in settings.items():
            _validate_setting(key, value)

        try:
            self._device_settings_request(method="patch", json_data=settings)

            self.update(device_settings_json=settings)
        except SkybellException as exc:
            _LOGGER.warning("Exception changing settings: %s", settings)
            _LOGGER.warning(exc)

    @property
    def name(self):
        """Get the name of this device."""
        return self._device_json.get(CONST.NAME)

    @property
    def type(self):
        """Get the type of this device."""
        return self._type

    @property
    def device_id(self):
        """Get the device id."""
        return self._device_id

    @property
    def status(self):
        """Get the generic status of a device (up/down)."""
        return self._device_json.get(CONST.STATUS)

    @property
    def is_up(self):
        """Shortcut to get if the device status is up."""
        return self.status == CONST.STATUS_UP

    @property
    def location(self):
        """Return lat and lng tuple."""
        location = self._device_json.get(CONST.LOCATION, {})

        return (location.get(CONST.LOCATION_LAT, 0),
                location.get(CONST.LOCATION_LNG, 0))

    @property
    def image(self):
        """Get the most recent 'avatar' image."""
        return self._device_json.get(CONST.AVATAR, {}).get(CONST.AVATAR_URL)

    @property
    def wifi_status(self):
        """Get the wifi status."""
        return self._device_info_json.get(
            CONST.STATUS, {}).get(CONST.WIFI_LINK)

    @property
    def wifi_ssid(self):
        """Get the wifi ssid."""
        return self._device_info_json.get(CONST.WIFI_SSID)

    @property
    def last_check_in(self):
        """Get last check in timestamp."""
        return self._device_info_json.get(CONST.CHECK_IN)

    @property
    def do_not_disturb(self):
        """Get if do not disturb is enabled."""
        return self._device_settings_json.get(CONST.SETTINGS_DO_NOT_DISTURB)

    @do_not_disturb.setter
    def do_not_disturb(self, enabled):
        """Set do not disturb."""
        self._set_setting({CONST.SETTINGS_DO_NOT_DISTURB: enabled})

    @property
    def outdoor_chime_level(self):
        """Get devices outdoor chime level."""
        return self._device_settings_json.get(CONST.SETTINGS_OUTDOOR_CHIME)

    @outdoor_chime_level.setter
    def outdoor_chime_level(self, level):
        """Set outdoor chime level."""
        self._set_setting({CONST.SETTINGS_OUTDOOR_CHIME: level})

    @property
    def outdoor_chime(self):
        """Get if the devices outdoor chime is enabled."""
        return self.outdoor_chime_level is not CONST.SETTINGS_OUTDOOR_CHIME_OFF

    @property
    def motion_sensor(self):
        """Get if the devices motion sensor is enabled."""
        return (
            self._device_settings_json.get(CONST.SETTINGS_MOTION_POLICY) ==
            CONST.SETTINGS_MOTION_POLICY_ON)

    @motion_sensor.setter
    def motion_sensor(self, enabled):
        """Set the motion sensor state."""
        if enabled is True:
            value = CONST.SETTINGS_MOTION_POLICY_ON
        elif enabled is False:
            value = CONST.SETTINGS_MOTION_POLICY_OFF
        else:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (CONST.SETTINGS_MOTION_POLICY, enabled))

        self._set_setting({CONST.SETTINGS_MOTION_POLICY: value})

    @property
    def motion_threshold(self):
        """Get devices motion threshold."""
        return self._device_settings_json.get(CONST.SETTINGS_MOTION_THRESHOLD)

    @motion_threshold.setter
    def motion_threshold(self, threshold):
        """Set motion threshold."""
        self._set_setting({CONST.SETTINGS_MOTION_THRESHOLD: threshold})

    @property
    def video_profile(self):
        """Get devices video profile."""
        return self._device_settings_json.get(CONST.SETTINGS_VIDEO_PROFILE)

    @video_profile.setter
    def video_profile(self, profile):
        """Set video profile."""
        self._set_setting({CONST.SETTINGS_VIDEO_PROFILE: profile})

    @property
    def led_rgb(self):
        """Get devices LED color."""
        return (self._device_settings_json.get(CONST.SETTINGS_LED_R),
                self._device_settings_json.get(CONST.SETTINGS_LED_G),
                self._device_settings_json.get(CONST.SETTINGS_LED_B))

    @led_rgb.setter
    def led_rgb(self, color):
        """Set devices LED color."""
        if (not isinstance(color, (list, tuple)) or
                not all(isinstance(item, int) for item in color)):
            raise SkybellException(ERROR.COLOR_VALUE_NOT_VALID, color)

        self._set_setting(
            {
                CONST.SETTINGS_LED_R: color[0],
                CONST.SETTINGS_LED_G: color[1],
                CONST.SETTINGS_LED_B: color[2]
            })

    @property
    def led_intensity(self):
        """Get devices LED intensity."""
        return self._device_settings_json.get(CONST.SETTINGS_LED_INTENSITY)

    @led_intensity.setter
    def led_intensity(self, intensity):
        """Set devices LED intensity."""
        self._set_setting({CONST.SETTINGS_LED_INTENSITY: intensity})

    @property
    def desc(self):
        """Get a short description of the device."""
        # Front Door (id: ) - skybell hd - status: up - wifi status: good
        return '{0} (id: {1}) - {2} - status: {3} - wifi status: {4}'.format(
            self.name, self.device_id, self.type,
            self.status, self.wifi_status)


def _validate_setting(setting, value):
    """Validate the setting and value."""
    if setting not in CONST.ALL_SETTINGS:
        raise SkybellException(ERROR.INVALID_SETTING, setting)

    if setting == CONST.SETTINGS_DO_NOT_DISTURB:
        if value not in CONST.SETTINGS_DO_NOT_DISTURB_VALUES:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting == CONST.SETTINGS_OUTDOOR_CHIME:
        if value not in CONST.SETTINGS_OUTDOOR_CHIME_VALUES:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting == CONST.SETTINGS_MOTION_POLICY:
        if value not in CONST.SETTINGS_MOTION_POLICY_VALUES:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting == CONST.SETTINGS_MOTION_THRESHOLD:
        if value not in CONST.SETTINGS_MOTION_THRESHOLD_VALUES:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting == CONST.SETTINGS_VIDEO_PROFILE:
        if value not in CONST.SETTINGS_VIDEO_PROFILE_VALUES:
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting in CONST.SETTINGS_LED_COLOR:
        if (value < CONST.SETTINGS_LED_VALUES[0] or
                value > CONST.SETTINGS_LED_VALUES[1]):
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))

    if setting == CONST.SETTINGS_LED_INTENSITY:
        if not isinstance(value, int):
            raise SkybellException(ERROR.COLOR_INTENSITY_NOT_VALID, value)

        if (value < CONST.SETTINGS_LED_INTENSITY_VALUES[0] or
                value > CONST.SETTINGS_LED_INTENSITY_VALUES[1]):
            raise SkybellException(ERROR.INVALID_SETTING_VALUE,
                                   (setting, value))
