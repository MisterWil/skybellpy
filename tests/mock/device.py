"""Mock Skybell Device Response."""

from tests.mock import USERID

DEVID = 'devid123abc'

def get_response_ok(user_id=USERID, name='Front Door', dev_id=DEVID):
    """Return the successful device response json."""
    return '''
    {
        "user": "'''+user_id+'''",
        "uuid": "devuuid123",
        "resourceId": "devresourceid123",
        "deviceInviteToken": "devInviteToken123",
        "location": {
            "lat": "-0.0",
            "lng": "0.0"
        },
        "name": "'''+name+'''",
        "type": "skybell hd",
        "status": "up",
        "createdAt": "2016-12-03T16:48:13.651Z",
        "updatedAt": "2017-09-25T23:32:45.374Z",
        "timeZone": {
            "dstOffset": 3600,
            "rawOffset": 36000,
            "status": "OK",
            "timeZoneId": "Australia/Sydney",
            "timeZoneName": "Australian Eastern Daylight Time"
        },
        "avatar": {
            "bucket": "v3-production-devices-avatar",
            "key": "path/key123.jpg",
            "createdAt": "2017-09-25T23:32:45.312Z",
            "url": "http://www.google.com/"
        },
        "id": "'''+dev_id+'''",
        "acl": "owner"
    }'''