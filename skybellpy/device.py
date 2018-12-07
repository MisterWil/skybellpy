"""The device class used by SkybellPy."""
import json
import logging

from distutils.util import strtobool

from skybellpy.exceptions import SkybellException
import skybellpy.helpers.constants as CONST
import skybellpy.helpers.errors as ERROR
import skybellpy.utils as UTILS

_LOGGER = logging.getLogger(__name__)


class SkybellDevice(object):
    """Class to represent each Skybell device."""

    def __init__(self, device_json, skybell):
        """Set up Skybell device."""
        self._device_json = device_json
        self._device_id = device_json.get(CONST.ID)
        self._type = device_json.get(CONST.TYPE)
        self._skybell = skybell

        self._info_json = self._info_request()
        self._settings_json = self._settings_request()

        self._update_activities()

    def refresh(self):
        """Refresh the devices json object data."""
        # Update core device data
        new_device_json = self._device_request()
        _LOGGER.debug("Device Refresh Response: %s", new_device_json)

        # Update device detail info
        new_info_json = self._info_request()
        _LOGGER.debug("Device Info Refresh Response: %s", new_info_json)

        # Update device setting details
        new_settings_json = self._settings_request()
        _LOGGER.debug("Device Settings Refresh Response: %s",
                      new_settings_json)

        # Update the stored data
        self.update(new_device_json, new_info_json, new_settings_json)

        # Update the activities
        self._update_activities()

    def _device_request(self):
        url = str.replace(CONST.DEVICE_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def _info_request(self):
        url = str.replace(CONST.DEVICE_INFO_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def _settings_request(self, method="get", json_data=None):
        url = str.replace(CONST.DEVICE_SETTINGS_URL, '$DEVID$', self.device_id)
        response = self._skybell.send_request(method=method,
                                              url=url,
                                              json_data=json_data)
        return json.loads(response.text)

    def _activities_request(self):
        url = str.replace(CONST.DEVICE_ACTIVITIES_URL,
                          '$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def update(self, device_json=None, info_json=None, settings_json=None):
        """Update the internal device json data."""
        if device_json:
            UTILS.update(self._device_json, device_json)

        if info_json:
            UTILS.update(self._info_json, info_json)

        if settings_json:
            UTILS.update(self._settings_json, settings_json)

    def _update_activities(self):
        """Update stored activities and update caches as required."""
        self._activities = self._activities_request()
        _LOGGER.debug("Device Activities Response: %s", self._activities)

        if not self._activities:
            self._activities = []
        elif not isinstance(self._activities, (list, tuple)):
            self._activities = [self._activities]

        self._update_events()

    def _update_events(self):
        """Update our cached list of latest activity events."""
        events = self._skybell.dev_cache(self, CONST.EVENT) or {}

        for activity in self._activities:
            event = activity.get(CONST.EVENT)
            created_at = activity.get(CONST.CREATED_AT)

            old_event = events.get(event)

            if old_event and created_at < old_event.get(CONST.CREATED_AT):
                continue
            else:
                events[event] = activity

        self._skybell.update_dev_cache(
            self,
            {
                CONST.EVENT: events
            })

    def activities(self, limit=1, event=None):
        """Return device activity information."""
        activities = self._activities or []

        # Filter our activity array if requested
        if event:
            activities = list(
                filter(
                    lambda activity:
                    activity[CONST.EVENT] == event, activities))

        # Return the requested number
        return activities[:limit]

    def latest(self, event=None):
        """Return the latest event activity."""
        events = self._skybell.dev_cache(self, CONST.EVENT) or {}
        _LOGGER.debug(events)

        if event:
            return events.get(event)

        latest = None
        for _, evt in events.items():
            if not latest or \
                    latest.get(CONST.CREATED_AT) < evt.get(CONST.CREATED_AT):
                latest = evt
        return latest

    def _set_setting(self, settings):
        """Validate the settings and then send the PATCH request."""
        for key, value in settings.items():
            _validate_setting(key, value)

        try:
            self._settings_request(method="patch", json_data=settings)

            self.update(settings_json=settings)
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
        # avatar AWS url stopped working October 2018
        # switched to last activity url
        # return self._device_json.get(CONST.AVATAR, {}).get(CONST.AVATAR_URL)
        return self.latest().get(CONST.MEDIA_URL)

    @property
    def wifi_status(self):
        """Get the wifi status."""
        return self._info_json.get(CONST.STATUS, {}).get(CONST.WIFI_LINK)

    @property
    def wifi_ssid(self):
        """Get the wifi ssid."""
        return self._info_json.get(CONST.WIFI_SSID)

    @property
    def last_check_in(self):
        """Get last check in timestamp."""
        return self._info_json.get(CONST.CHECK_IN)

    @property
    def do_not_disturb(self):
        """Get if do not disturb is enabled."""
        return bool(strtobool(str(self._settings_json.get(
            CONST.SETTINGS_DO_NOT_DISTURB))))

    @do_not_disturb.setter
    def do_not_disturb(self, enabled):
        """Set do not disturb."""
        self._set_setting(
            {
                CONST.SETTINGS_DO_NOT_DISTURB: str(enabled).lower()
            })

    @property
    def outdoor_chime_level(self):
        """Get devices outdoor chime level."""
        return self._settings_json.get(CONST.SETTINGS_OUTDOOR_CHIME)

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
            self._settings_json.get(CONST.SETTINGS_MOTION_POLICY) ==
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
        return self._settings_json.get(CONST.SETTINGS_MOTION_THRESHOLD)

    @motion_threshold.setter
    def motion_threshold(self, threshold):
        """Set motion threshold."""
        self._set_setting({CONST.SETTINGS_MOTION_THRESHOLD: threshold})

    @property
    def video_profile(self):
        """Get devices video profile."""
        return self._settings_json.get(CONST.SETTINGS_VIDEO_PROFILE)

    @video_profile.setter
    def video_profile(self, profile):
        """Set video profile."""
        self._set_setting({CONST.SETTINGS_VIDEO_PROFILE: profile})

    @property
    def led_rgb(self):
        """Get devices LED color."""
        return (int(self._settings_json.get(CONST.SETTINGS_LED_R)),
                int(self._settings_json.get(CONST.SETTINGS_LED_G)),
                int(self._settings_json.get(CONST.SETTINGS_LED_B)))

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
        return int(self._settings_json.get(CONST.SETTINGS_LED_INTENSITY))

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
