"""skybellpy constants."""
import os

MAJOR_VERSION = 0
MINOR_VERSION = 1
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

COOKIES_PATH = './skybell_cookies.pickle'

# URLS
BASE_URL = 'https://cloud.myskybell.com/api/v3/'

LOGIN_URL = BASE_URL + 'login/'
LOGOUT_URL = BASE_URL + 'logout/'

USERS_ME_URL = BASE_URL + 'users/me/'

DEVICES_URL = BASE_URL + 'devices/'
DEVICE_URL = DEVICES_URL + '$DEVID$/'
DEVICE_ACTIVITIES_URL = DEVICE_URL + 'activities/'
DEVICE_AVATAR_URL = DEVICE_URL + 'avatar/'

SUBSCRIPTIONS_URL = BASE_URL + 'subscriptions/?include=owner'
SUBSCRIPTION_URL = BASE_URL + 'subscriptions/$SUBSCRIPTIONID$/'
SUBSCRIPTION_INFO_URL = SUBSCRIPTION_URL + '/info/'
SUBSCRIPTION_SETTINGS_URL = SUBSCRIPTION_URL + '/settings/'
