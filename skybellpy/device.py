"""The device class used by SkybellPy."""
import json
import logging

import skybellpy.helpers.constants as CONST

_LOGGER = logging.getLogger(__name__)


class SkybellDevice(object):
    """Class to represent each Skybell device."""

    def __init__(self, device_json, skybell):
        """Set up Skybell device."""
        self._device_json = device_json
        self._device_id = device_json.get('id')
        self._type = device_json.get('type')
        self._skybell = skybell

        self._device_info_json = self._get_device_info_json()

    def refresh(self):
        """Refresh the devices json object data."""
        new_device_json = self._get_device_json()
        _LOGGER.debug("Device Refresh Response: %s", new_device_json)

        new_device_info_json = self._get_device_info_json()
        _LOGGER.debug("Device Info Refresh Response: %s", new_device_info_json)

        self.update(new_device_json, new_device_info_json)

    def _get_device_json(self):
        url = CONST.DEVICE_URL.replace('$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def _get_device_info_json(self):
        url = CONST.DEVICE_INFO_URL.replace('$DEVID$', self.device_id)
        response = self._skybell.send_request(method="get", url=url)
        return json.loads(response.text)

    def update(self, device_json=None, device_info_json=None):
        """Update the json data from a dictionary.

        Only updates if it already exists in the device.
        """
        if device_json:
            self._device_json.update(
                {k: device_json[k] for k in device_json
                 if self._device_json.get(k)})

        if device_info_json:
            self._device_info_json.update(
                {k: device_info_json[k] for k in device_info_json
                 if self._device_info_json.get(k)})

    @property
    def name(self):
        """Get the name of this device."""
        return self._device_json.get('name')

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
        return self._device_json.get('status')

    @property
    def is_up(self):
        """Shortcut to get if the device status is up."""
        return self.status == 'up'

    @property
    def location(self):
        """Return lat and lng tuple."""
        location = self._device_json.get('location', {})

        return location.get('lat', 0), location.get('lng', 0)

    @property
    def image(self):
        """Get the most recent 'avatar' image."""
        return self._device_json.get('avatar', {}).get('url')

    @property
    def wifi_status(self):
        """Get the wifi status."""
        return self._device_info_json.get('status', {}).get('wifiLink')

    @property
    def wifi_ssid(self):
        """Get the wifi ssid."""
        return self._device_info_json.get('essid')

    @property
    def last_check_in(self):
        """Get last check in timestamp."""
        return self._device_info_json.get('checkedInAt')

    @property
    def desc(self):
        """Get a short description of the device."""
        # Front Door (id: ) - skybell hd - status: up - wifi status: good
        return '{0} (id: {1}) - {2} - status: {3} - wifi status: {4}'.format(
            self.name, self.device_id, self.type,
            self.status, self.wifi_status)
