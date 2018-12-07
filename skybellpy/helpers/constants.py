"""skybellpy constants."""
import os

MAJOR_VERSION = 0
MINOR_VERSION = 2
PATCH_VERSION = '0'

__version__ = '{}.{}.{}'.format(MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)

REQUIRED_PYTHON_VER = (3, 4, 2)

PROJECT_NAME = 'skybellpy'
PROJECT_PACKAGE_NAME = 'skybellpy'
PROJECT_LICENSE = 'MIT'
PROJECT_AUTHOR = 'Wil Schrader'
PROJECT_COPYRIGHT = ' 2017, {}'.format(PROJECT_AUTHOR)
PROJECT_URL = 'https://github.com/MisterWil/skybellpy'
PROJECT_EMAIL = 'wilrader@gmail.com'
PROJECT_DESCRIPTION = ('An Skybell HD Python library '
                       'running on Python 3.')
PROJECT_LONG_DESCRIPTION = ('skybellpy is an open-source '
                            'unofficial API for the Skybell HD '
                            'doorbell with the intention for easy '
                            'integration into various home '
                            'automation platforms.')
if os.path.exists('README.rst'):
    PROJECT_LONG_DESCRIPTION = open('README.rst').read()
PROJECT_CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.4',
    'Topic :: Home Automation'
]

PROJECT_GITHUB_USERNAME = 'MisterWil'
PROJECT_GITHUB_REPOSITORY = 'skybellpy'

PYPI_URL = 'https://pypi.python.org/pypi/{}'.format(PROJECT_PACKAGE_NAME)

CACHE_PATH = './skybell.pickle'

# URLS
BASE_URL = 'https://cloud.myskybell.com/api/v3/'
BASE_URL_V4 = 'https://cloud.myskybell.com/api/v4/'

LOGIN_URL = BASE_URL + 'login/'
LOGOUT_URL = BASE_URL + 'logout/'

USERS_ME_URL = BASE_URL + 'users/me/'

DEVICES_URL = BASE_URL + 'devices/'
DEVICE_URL = DEVICES_URL + '$DEVID$/'
DEVICE_ACTIVITIES_URL = DEVICE_URL + 'activities/'
DEVICE_AVATAR_URL = DEVICE_URL + 'avatar/'
DEVICE_INFO_URL = DEVICE_URL + 'info/'
DEVICE_SETTINGS_URL = DEVICE_URL + 'settings/'

SUBSCRIPTIONS_URL = BASE_URL + 'subscriptions?include=device,owner'
SUBSCRIPTION_URL = BASE_URL + 'subscriptions/$SUBSCRIPTIONID$'
SUBSCRIPTION_INFO_URL = SUBSCRIPTION_URL + '/info/'
SUBSCRIPTION_SETTINGS_URL = SUBSCRIPTION_URL + '/settings/'

# GENERAL
APP_ID = 'app_id'
CLIENT_ID = 'client_id'
TOKEN = 'token'
ACCESS_TOKEN = 'access_token'
DEVICES = 'devices'

# DEVICE
NAME = 'name'
ID = 'id'
TYPE = 'type'
STATUS = 'status'
STATUS_UP = 'up'
LOCATION = 'location'
LOCATION_LAT = 'lat'
LOCATION_LNG = 'lng'
AVATAR = 'avatar'
AVATAR_URL = 'url'
MEDIA_URL = 'media'

# DEVICE INFO
WIFI_LINK = 'wifiLink'
WIFI_SSID = 'essid'
CHECK_IN = 'checkedInAt'

# DEVICE ACTIVITIES
EVENT = 'event'
EVENT_ON_DEMAND = 'application:on-demand'
EVENT_BUTTON = 'device:sensor:button'
EVENT_MOTION = 'device:sensor:motion'
CREATED_AT = 'createdAt'

STATE = 'state'
STATE_READY = 'ready'

VIDEO_STATE = 'videoState'
VIDEO_STATE_READY = 'download:ready'

# DEVICE SETTINGS
SETTINGS_DO_NOT_DISTURB = 'do_not_disturb'
SETTINGS_OUTDOOR_CHIME = 'chime_level'
SETTINGS_MOTION_POLICY = 'motion_policy'
SETTINGS_MOTION_THRESHOLD = 'motion_threshold'
SETTINGS_VIDEO_PROFILE = 'video_profile'
SETTINGS_LED_R = 'green_r'
SETTINGS_LED_G = 'green_g'
SETTINGS_LED_B = 'green_b'
SETTINGS_LED_COLOR = [SETTINGS_LED_R, SETTINGS_LED_G, SETTINGS_LED_B]
SETTINGS_LED_INTENSITY = 'led_intensity'

ALL_SETTINGS = [SETTINGS_DO_NOT_DISTURB, SETTINGS_OUTDOOR_CHIME,
                SETTINGS_MOTION_POLICY, SETTINGS_MOTION_THRESHOLD,
                SETTINGS_VIDEO_PROFILE, SETTINGS_LED_R,
                SETTINGS_LED_G, SETTINGS_LED_B, SETTINGS_LED_INTENSITY]

# SETTINGS Values
SETTINGS_DO_NOT_DISTURB_VALUES = ["true", "false"]

SETTINGS_OUTDOOR_CHIME_OFF = 0
SETTINGS_OUTDOOR_CHIME_LOW = 1
SETTINGS_OUTDOOR_CHIME_MEDIUM = 2
SETTINGS_OUTDOOR_CHIME_HIGH = 3
SETTINGS_OUTDOOR_CHIME_VALUES = [SETTINGS_OUTDOOR_CHIME_OFF,
                                 SETTINGS_OUTDOOR_CHIME_LOW,
                                 SETTINGS_OUTDOOR_CHIME_MEDIUM,
                                 SETTINGS_OUTDOOR_CHIME_HIGH]

SETTINGS_MOTION_POLICY_OFF = 'disabled'
SETTINGS_MOTION_POLICY_ON = 'call'
SETTINGS_MOTION_POLICY_VALUES = [SETTINGS_MOTION_POLICY_OFF,
                                 SETTINGS_MOTION_POLICY_ON]

SETTINGS_MOTION_THRESHOLD_LOW = 100
SETTINGS_MOTION_THRESHOLD_MEDIUM = 50
SETTINGS_MOTION_THRESHOLD_HIGH = 32
SETTINGS_MOTION_THRESHOLD_VALUES = [SETTINGS_MOTION_THRESHOLD_LOW,
                                    SETTINGS_MOTION_THRESHOLD_MEDIUM,
                                    SETTINGS_MOTION_THRESHOLD_HIGH]

SETTINGS_VIDEO_PROFILE_1080P = 0
SETTINGS_VIDEO_PROFILE_720P_BETTER = 1
SETTINGS_VIDEO_PROFILE_720P_GOOD = 2
SETTINGS_VIDEO_PROFILE_480P = 3
SETTINGS_VIDEO_PROFILE_VALUES = [SETTINGS_VIDEO_PROFILE_1080P,
                                 SETTINGS_VIDEO_PROFILE_720P_BETTER,
                                 SETTINGS_VIDEO_PROFILE_720P_GOOD,
                                 SETTINGS_VIDEO_PROFILE_480P]

SETTINGS_LED_VALUES = [0, 255]

SETTINGS_LED_INTENSITY_VALUES = [0, 100]
