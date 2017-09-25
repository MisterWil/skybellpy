#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
skybellpy by Wil Schrader - An Abode alarm Python library.

https://github.com/MisterWil/skybellpy

Influenced by blinkpy, because I'm a python noob:
https://github.com/fronzbot/blinkpy/

Published under the MIT license - See LICENSE file for more details.

"Skybell" is a trademark owned by SkyBell Technologies, Inc, see www.skybell.com for
more information. I am in no way affiliated with Skybell.
"""
import os.path
import json
import logging
import pickle
import uuid
import random
import string
import requests
from requests.exceptions import RequestException

from skybellpy.exceptions import SkybellAuthenticationException, SkybellException
import skybellpy.helpers.constants as CONST
import skybellpy.helpers.errors as ERROR

_LOGGER = logging.getLogger(__name__)


def _save_cookies(data, filename):
    """Save cookies to a file."""
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle)


def _load_cookies(filename):
    """Load cookies from a file."""
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def _gen_token():
    return ''.join(
        random.choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(32))


class Skybell():
    """Main Skybell class."""

    def __init__(self, username=None, password=None,
                 auto_login=False, get_devices=False,
                 disable_cookies=False):
        """Init Abode object."""
        self._username = username
        self._password = password
        self._session = None
        self._cookies = None

        self._devices = None

        # Create a requests session to persist the cookies
        self._session = requests.session()

        # Load App ID, Client ID, and Token
        if not disable_cookies and os.path.exists(CONST.COOKIES_PATH):
            _LOGGER.debug("Cookies found at: %s", CONST.COOKIES_PATH)
            self._cookies = _load_cookies(CONST.COOKIES_PATH)
        else:
            self._cookies = {
                'app_id': str(uuid.uuid4()),
                'client_id': str(uuid.uuid4()),
                'token': _gen_token(),
                'access_token': None
            }

        if (self._username is not None and
                self._password is not None and
                auto_login):
            self.login()

        if get_devices:
            self.get_devices()

    def login(self, username=None, password=None):
        """Execute Skybell login."""
        if username is not None:
            self._username = username
        if password is not None:
            self._password = password

        if self._username is None or not isinstance(self._username, str):
            raise SkybellAuthenticationException(ERROR.USERNAME)

        if self._password is None or not isinstance(self._password, str):
            raise SkybellAuthenticationException(ERROR.PASSWORD)

        self._cookies['access_token'] = None

        login_data = {
            'username': self._username,
            'password': self._password,
            'appId': self._cookies['app_id'],
            'token': self._cookies['token']
        }

        response = self.send_request('post', CONST.LOGIN_URL,
                                     json_data=login_data, retry=False)

        if response.status_code != 200:
            raise SkybellAuthenticationException((response.status_code,
                                                  response.text))

        _LOGGER.debug("Login Response: %s", response.text)

        response_object = json.loads(response.text)

        self._cookies['access_token'] = response_object['access_token']

        _save_cookies(self._cookies, CONST.COOKIES_PATH)

        _LOGGER.info("Login successful")

        return True

    def logout(self):
        """Explicit Skybell logout."""
        if self._cookies['access_token']:
            # No explicit logout call as it doesn't seem to matter
            # if a logout happens without registering the app which
            # we aren't currently doing.
            self._session = requests.session()
            self._devices = None

        return True

    def get_devices(self, refresh=False):
        """Get all devices from Abode."""
        if refresh or self._devices is None:
            if self._devices is None:
                self._devices = {}

            _LOGGER.info("Updating all devices...")
            response = self.send_request("get", CONST.DEVICES_URL)
            response_object = json.loads(response.text)

            if (response_object and
                    not isinstance(response_object, (tuple, list))):
                response_object = [response_object]

            _LOGGER.debug("Get Devices Response: %s", response.text)

            for device_json in response_object:
                # Attempt to reuse an existing device
                device = self._devices.get(device_json['id'])

                # No existing device, create a new one
                if device:
                    device.update(device_json)
                else:
                    device = SkybellDevice(device_json, self)
                    self._devices[device.device_id] = device

        return list(self._devices.values())

    def get_device(self, device_id, refresh=False):
        """Get a single device."""
        if self._devices is None:
            self.get_devices()
            refresh = False

        device = self._devices.get(device_id)

        if device and refresh:
            device.refresh()

        return device

    def send_request(self, method, url, headers=None,
                     json_data=None, retry=True):
        """Send requests to Skybell."""
        if not headers:
            headers = {}

        if self._cookies['access_token']:
            headers['Authorization'] = 'Bearer ' + self._cookies['access_token']

        headers['user-agent'] = 'SkyBell/3.4.1 (iPhone9,2; iOS 11.0; loc=en_US; lang=en-US) com.skybell.doorbell/1'
        headers['content-type'] = 'application/json'
        headers['accepts'] = '*/*'
        headers['x-skybell-app-id'] = self._cookies['app_id']
        headers['x-skybell-client-id'] = self._cookies['client_id']

        try:
            response = getattr(self._session, method)(
                url, headers=headers, json=json_data)

            if response and response.status_code < 400:
                return response
        except RequestException as exc:
            _LOGGER.warning("Skybell requext exception: %s", exc)

        if retry:
            self.login()

            return self.send_request(method, url, headers, json_data, False)

        raise SkybellException((ERROR.REQUEST))


class SkybellDevice(object):
    """Class to represent each Skybell device."""

    def __init__(self, json_obj, skybell):
        """Set up Skybell device."""
        self._json_state = json_obj
        self._device_id = json_obj.get('id')
        self._name = json_obj.get('name')
        self._type = json_obj.get('type')
        self._skybell = skybell

        if not self._name:
            self._name = self.type + ' ' + self.device_id

    def get_value(self, name):
        """Get a value from the json object.

        This is the common data and is the best place to get state
        from if it has the data you require.
        This data is updated by the subscription service.
        """
        return self._json_state.get(name.lower(), {})

    def refresh(self, url=CONST.DEVICE_URL):
        """Refresh the devices json object data.

        Only needed if you're not using the notification service.
        """
        url = url.replace('$DEVID$', self.device_id)

        response = self._skybell.send_request(method="get", url=url)
        response_object = json.loads(response.text)

        _LOGGER.debug("Device Refresh Response: %s", response.text)

        if response_object and not isinstance(response_object, (tuple, list)):
            response_object = [response_object]

        for device in response_object:
            self.update(device)

        return response_object

    def update(self, json_state):
        """Update the json data from a dictionary.

        Only updates if it already exists in the device.
        """
        self._json_state.update(
            {k: json_state[k] for k in json_state if self._json_state.get(k)})

    @property
    def status(self):
        """Shortcut to get the generic status of a device."""
        return self.get_value('status')

    @property
    def level(self):
        """Shortcut to get the generic level of a device."""
        return self.get_value('level')

    @property
    def battery_low(self):
        """Is battery level low."""
        return int(self.get_value('faults').get('low_battery', '0')) == 1

    @property
    def no_response(self):
        """Is the device responding."""
        return int(self.get_value('faults').get('no_response', '0')) == 1

    @property
    def out_of_order(self):
        """Is the device out of order."""
        return int(self.get_value('faults').get('out_of_order', '0')) == 1

    @property
    def tampered(self):
        """Has the device been tampered with."""
        # 'tempered' - Typo in API?
        return int(self.get_value('faults').get('tempered', '0')) == 1

    @property
    def name(self):
        """Get the name of this device."""
        return self._name

    @property
    def type(self):
        """Get the type of this device."""
        return self._type

    @property
    def device_id(self):
        """Get the device id."""
        return self._device_id

    @property
    def desc(self):
        """Get a short description of the device."""
        # Garage Entry Door (ZW:00000003) - Door Lock - Closed
        return '{0} (ID: {1}) - {2} - {3}'.format(
            self.name, self.device_id, self.type, self.status)
