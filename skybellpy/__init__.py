#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
skybellpy by Wil Schrader - An Abode alarm Python library.

https://github.com/MisterWil/skybellpy

Influenced by blinkpy, because I'm a python noob:
https://github.com/fronzbot/blinkpy/

Published under the MIT license - See LICENSE file for more details.

"Skybell" is a trademark owned by SkyBell Technologies, Inc, see
www.skybell.com for more information. I am in no way affiliated with Skybell.
"""
import os.path
import json
import logging
import requests
from requests.exceptions import RequestException

from skybellpy.device import SkybellDevice
from skybellpy.exceptions import (
    SkybellAuthenticationException, SkybellException)
import skybellpy.helpers.constants as CONST
import skybellpy.helpers.errors as ERROR
import skybellpy.utils as UTILS

_LOGGER = logging.getLogger(__name__)


class Skybell():
    """Main Skybell class."""

    def __init__(self, username=None, password=None,
                 auto_login=False, get_devices=False,
                 cache_path=CONST.CACHE_PATH, disable_cache=False):
        """Init Abode object."""
        self._username = username
        self._password = password
        self._session = None
        self._cache_path = cache_path
        self._disable_cache = disable_cache
        self._devices = None
        self._session = requests.session()

        # Create a new cache template
        self._cache = {
            CONST.APP_ID: UTILS.gen_id(),
            CONST.CLIENT_ID: UTILS.gen_id(),
            CONST.TOKEN: UTILS.gen_token(),
            CONST.ACCESS_TOKEN: None,
            CONST.DEVICES: {}
        }

        # Load and merge an existing cache
        if not disable_cache:
            self._load_cache()

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

        self.update_cache(
            {
                CONST.ACCESS_TOKEN: None
            })

        login_data = {
            'username': self._username,
            'password': self._password,
            'appId': self.cache(CONST.APP_ID),
            CONST.TOKEN: self.cache(CONST.TOKEN)
        }

        try:
            response = self.send_request('post', CONST.LOGIN_URL,
                                         json_data=login_data, retry=False)
        except Exception as exc:
            raise SkybellAuthenticationException(ERROR.LOGIN_FAILED, exc)

        _LOGGER.debug("Login Response: %s", response.text)

        response_object = json.loads(response.text)

        self.update_cache({
            CONST.ACCESS_TOKEN: response_object[CONST.ACCESS_TOKEN]})

        _LOGGER.info("Login successful")

        return True

    def logout(self):
        """Explicit Skybell logout."""
        if self.cache(CONST.ACCESS_TOKEN):
            # No explicit logout call as it doesn't seem to matter
            # if a logout happens without registering the app which
            # we aren't currently doing.
            self._session = requests.session()
            self._devices = None

            self.update_cache({CONST.ACCESS_TOKEN: None})

        return True

    def get_devices(self, refresh=False):
        """Get all devices from Abode."""
        if refresh or self._devices is None:
            if self._devices is None:
                self._devices = {}

            _LOGGER.info("Updating all devices...")
            response = self.send_request("get", CONST.DEVICES_URL)
            response_object = json.loads(response.text)

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
        if not self.cache(CONST.ACCESS_TOKEN) and url != CONST.LOGIN_URL:
            self.login()

        if not headers:
            headers = {}

        if self.cache(CONST.ACCESS_TOKEN):
            headers['Authorization'] = 'Bearer ' + \
                self.cache(CONST.ACCESS_TOKEN)

        headers['user-agent'] = (
            'SkyBell/3.4.1 (iPhone9,2; iOS 11.0; loc=en_US; lang=en-US) '
            'com.skybell.doorbell/1')
        headers['content-type'] = 'application/json'
        headers['accepts'] = '*/*'
        headers['x-skybell-app-id'] = self.cache(CONST.APP_ID)
        headers['x-skybell-client-id'] = self.cache(CONST.CLIENT_ID)

        _LOGGER.debug("HTTP %s %s Request with headers: %s",
                      method, url, headers)

        try:
            response = getattr(self._session, method)(
                url, headers=headers, json=json_data)
            _LOGGER.debug("%s %s", response, response.text)

            if response and response.status_code < 400:
                return response
        except RequestException as exc:
            _LOGGER.warning("Skybell request exception: %s", exc)

        if retry:
            self.login()

            return self.send_request(method, url, headers, json_data, False)

        raise SkybellException(ERROR.REQUEST, "Retry failed")

    def cache(self, key):
        """Get a cached value."""
        return self._cache.get(key)

    def update_cache(self, data):
        """Update a cached value."""
        UTILS.update(self._cache, data)
        self._save_cache()

    def dev_cache(self, device, key=None):
        """Get a cached value for a device."""
        device_cache = self._cache.get(CONST.DEVICES, {}).get(device.device_id)

        if device_cache and key:
            return device_cache.get(key)

        return device_cache

    def update_dev_cache(self, device, data):
        """Update cached values for a device."""
        self.update_cache(
            {
                CONST.DEVICES: {
                    device.device_id: data
                }
            })

    def _load_cache(self):
        """Load existing cache and merge for updating if required."""
        if not self._disable_cache and os.path.exists(self._cache_path):
            _LOGGER.debug("Cache found at: %s", self._cache_path)
            loaded_cache = UTILS.load_cache(self._cache_path)

            UTILS.update(self._cache, loaded_cache)

        self._save_cache()

    def _save_cache(self):
        """Trigger a cache save."""
        if not self._disable_cache:
            UTILS.save_cache(self._cache, self._cache_path)
