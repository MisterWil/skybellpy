"""Mock Skybell Device Activities Response."""

import skybellpy.helpers.constants as CONST
import tests.mock.device as DEVICE

EMPTY_ACTIVITIES_RESPONSE = '[]'


def get_response_ok(dev_id=DEVICE.DEVID,
                    event=CONST.EVENT_BUTTON,
                    state=CONST.STATE_READY,
                    video_state=CONST.VIDEO_STATE_READY):
    """Return the device activity response json."""
    return '''
    {
        "_id": "activityId",
        "updatedAt": "2017-09-28T21:50:41.740Z",
        "createdAt": "2017-09-28T21:50:41.740Z",
        "device": "''' + dev_id + '''",
        "callId": "activityCallId",
        "event": "''' + event + '''",
        "state": "''' + state + '''",
        "ttlStartDate": "2017-09-28T21:50:41.739Z",
        "videoState": "''' + video_state + '''",
        "id": "activityId",
        "media": "http://www.image.com/image.jpg",
        "mediaSmall": "http://www.image.com/image.jpg"
      }'''
