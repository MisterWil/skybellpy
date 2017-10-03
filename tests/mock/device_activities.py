"""Mock Skybell Device Activities Response."""

import datetime

import skybellpy.helpers.constants as CONST
import tests.mock.device as DEVICE

EMPTY_ACTIVITIES_RESPONSE = '[]'


def get_response_ok(dev_id=DEVICE.DEVID,
                    event=CONST.EVENT_BUTTON,
                    state=CONST.STATE_READY,
                    video_state=CONST.VIDEO_STATE_READY,
                    created_at=datetime.datetime.now()):
    """Return the device activity response json."""
    str_created_at = created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    return '''
    {
        "_id": "activityId",
        "updatedAt": "''' + str_created_at + '''",
        "createdAt": "''' + str_created_at + '''",
        "device": "''' + dev_id + '''",
        "callId": "''' + str_created_at + '''",
        "event": "''' + event + '''",
        "state": "''' + state + '''",
        "ttlStartDate": "''' + str_created_at + '''",
        "videoState": "''' + video_state + '''",
        "id": "activityId",
        "media": "http://www.image.com/image.jpg",
        "mediaSmall": "http://www.image.com/image.jpg"
      }'''
