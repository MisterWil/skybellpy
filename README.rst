skybell-python |Build Status| |Coverage Status|
=================================================
A thin Python library for the Skybell HD API.
Only compatible with Python 3+

Disclaimer:
~~~~~~~~~~~~~~~
Published under the MIT license - See LICENSE file for more details.

"Skybell" is a trademark owned by SkyBell Technologies, Inc, see www.skybell.com for more information.
I am in no way affiliated with Skybell.

Thank you Skybell for having a relatively simple API to reverse engineer. Hopefully in the future you'll
open it up for official use.

API calls faster than 60 seconds is not recommended as it can overwhelm Skybell's servers.

Please use this module responsibly.

Installation
============
From PyPi:

    pip3 install skybellpy
  
Command Line Usage
==================
Simple command line implementation arguments::

    $ skybellpy --help
      usage: SkybellPy: Command Line Utility [-h] -u USERNAME -p PASSWORD [--mode]
                                           [--devices] [--device device_id]
      
      optional arguments:
        -h, --help            show this help message and exit
        -u USERNAME, --username USERNAME
                              Username
        -p PASSWORD, --password PASSWORD
                              Password
        --devices             Output all devices
        --device device_id    Output one device for device_id

You can get all device information::

    $ skybellpy -u USERNAME -p PASSWORD --devices
    
      Output here

Development and Testing
=======================

Install the core dependencies::

    $ sudo apt-get install python3-pip python3-dev python3-venv

Checkout from github and then create a virtual environment::

    $ git clone https://github.com/MisterWil/skybellpy.git
    $ cd skybellpy
    $ python3 -m venv venv
    
Activate the virtual environment::

    $ source venv/bin/activate

Install requirements::

    $ pip install -r requirements.txt -r requirements_test.txt 
    
Install skybellpy locally in "editable mode"::

    $ pip3 install -e .
    
Run the run the full test suite with tox before commit::

    $ tox
    
Alternatively you can run just the tests::

    $ tox -e py35

Library Usage
=============
TODO

Class Descriptions
==================
TODO

.. |Build Status| image:: https://travis-ci.org/MisterWil/skybellpy.svg?branch=master
    :target: https://travis-ci.org/MisterWil/skybellpy
.. |Coverage Status| image:: https://coveralls.io/repos/github/MisterWil/skybellpy/badge.svg
    :target: https://coveralls.io/github/MisterWil/skybellpy
