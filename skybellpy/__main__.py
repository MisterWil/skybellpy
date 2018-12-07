#!/usr/bin/python
"""
skybellcl by Wil Schrader - A Skybell Python library command line interface.

https://github.com/MisterWil/skybellpy

Published under the MIT license - See LICENSE file for more details.

"Skybell" is a trademark owned by SkyBell Technologies, Inc, see
www.skybell.com for more information. I am in no way affiliated with Skybell.
"""
import json
import logging

import argparse

import skybellpy
import skybellpy.helpers.constants as CONST
from skybellpy.exceptions import SkybellException

_LOGGER = logging.getLogger('skybellcl')


def setup_logging(log_level=logging.INFO):
    """Set up the logging."""
    logging.basicConfig(level=log_level)
    fmt = ("%(asctime)s %(levelname)s (%(threadName)s) "
           "[%(name)s] %(message)s")
    colorfmt = "%(log_color)s{}%(reset)s".format(fmt)
    datefmt = '%Y-%m-%d %H:%M:%S'

    # Suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)

    try:
        from colorlog import ColoredFormatter
        logging.getLogger().handlers[0].setFormatter(ColoredFormatter(
            colorfmt,
            datefmt=datefmt,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
        ))
    except ImportError:
        pass

    logger = logging.getLogger('')
    logger.setLevel(log_level)


def get_arguments():
    """Get parsed arguments."""
    parser = argparse.ArgumentParser("SkybellPy: Command Line Utility")

    parser.add_argument(
        '-u', '--username',
        help='Username',
        required=True)

    parser.add_argument(
        '-p', '--password',
        help='Password',
        required=True)

    parser.add_argument(
        '--set',
        metavar='setting=value',
        help='Set setting to a value',
        required=False, action='append')

    parser.add_argument(
        '--devices',
        help='Output all devices',
        required=False, default=False, action="store_true")

    parser.add_argument(
        '--device',
        metavar='device_id',
        help='Output one device for device_id',
        required=False, action='append')

    parser.add_argument(
        '--json',
        metavar='device_id',
        help='Output the json for device_id',
        required=False, action='append')

    parser.add_argument(
        '--last-json',
        metavar='device_id',
        help='Output the last activity json for device_id',
        required=False, action='append')

    parser.add_argument(
        '--last-image',
        metavar='device_id',
        help='Output the last activity image url for device_id',
        required=False, action='append')

    parser.add_argument(
        '--capture',
        metavar='device_id',
        help='NOT IMPLEMENTED: '
             'Trigger a new image capture for the given device_id',
        required=False, action='append')

    parser.add_argument(
        '--image',
        metavar='device_id=location/image.jpg',
        help='NOT IMPLEMENTED: '
             'Save an image from a camera (if available) to the given path',
        required=False, action='append')

    parser.add_argument(
        '--debug',
        help='Enable debug logging',
        required=False, default=False, action="store_true")

    parser.add_argument(
        '--quiet',
        help='Output only warnings and errors',
        required=False, default=False, action="store_true")

    return parser.parse_args()


def call():
    """Execute command line helper."""
    args = get_arguments()

    # Set up logging
    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARN
    else:
        log_level = logging.INFO

    setup_logging(log_level)

    skybell = None

    try:
        # Create skybellpy instance.
        skybell = skybellpy.Skybell(username=args.username,
                                    password=args.password,
                                    get_devices=True)

    # # Set setting
    # for setting in args.set or []:
    #     keyval = setting.split("=")
    #     if skybell.set_setting(keyval[0], keyval[1]):
    #         _LOGGER.info("Setting %s changed to %s", keyval[0], keyval[1])

        # Output Json
        for device_id in args.json or []:
            device = skybell.get_device(device_id)

            if device:
                # pylint: disable=protected-access
                _LOGGER.info(device_id + " JSON:\n" +
                             json.dumps(device._device_json, sort_keys=True,
                                        indent=4, separators=(',', ': ')))
            else:
                _LOGGER.warning("Could not find device with id: %s", device_id)

        # Print
        def _device_print(dev, append=''):
            _LOGGER.info("%s%s",
                         dev.desc, append)

        # Print out all devices.
        if args.devices:
            for device in skybell.get_devices():
                _device_print(device)

        # Print out specific devices by device id.
        if args.device:
            for device_id in args.device:
                device = skybell.get_device(device_id)

                if device:
                    _device_print(device)
                else:
                    _LOGGER.warning(
                        "Could not find device with id: %s", device_id)

        # Print out last motion event
        if args.last_json:
            for device_id in args.last_json:
                device = skybell.get_device(device_id)

                if device:
                    _LOGGER.info(device.latest(CONST.EVENT_MOTION))
                else:
                    _LOGGER.warning(
                        "Could not find device with id: %s", device_id)

        # Print out last motion event
        if args.last_image:
            for device_id in args.last_image:
                device = skybell.get_device(device_id)

                if device:
                    _LOGGER.info(device.image)
                else:
                    _LOGGER.warning(
                        "Could not find device with id: %s", device_id)

    except SkybellException as exc:
        _LOGGER.error(exc)
    # finally:
        # if skybell:
        # skybell.logout()


def main():
    """Execute from command line."""
    call()


if __name__ == '__main__':
    main()
