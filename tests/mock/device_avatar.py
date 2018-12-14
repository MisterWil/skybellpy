"""Mock Skybell Device Avatar Response."""


def get_response_ok(data=''):
    """Return the successful device info response json."""
    return '''
    {
      "createdAt": "2018-12-14T21:20:06.198Z",
      "url":
      "https://v3-production-devices-avatar.s3-us-west-2.amazonaws.com/''' + \
           data + '''"
    }'''
