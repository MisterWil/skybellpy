"""Mock Skybell Device Info Response."""

import skybellpy.helpers.constants as CONST

PATCH_RESPONSE_OK = '{}'

PATHCH_RESPONSE_BAD_REQUEST = ''


def get_response_ok(do_not_disturb=False,
                    outdoor_chime=CONST.SETTINGS_OUTDOOR_CHIME_HIGH,
                    motion_policy=CONST.SETTINGS_MOTION_POLICY_ON,
                    motion_threshold=CONST.SETTINGS_MOTION_THRESHOLD_HIGH,
                    video_profile=CONST.SETTINGS_VIDEO_PROFILE_720P_BETTER,
                    led_rgb=(255, 255, 255),
                    led_intensity=100):
    """Return the successful device info response json."""
    return '''
    {
      "ring_tone": 0,
      "do_not_ring": false,
      "do_not_disturb": ''' + str(do_not_disturb).lower() + ''',
      "digital_doorbell": false,
      "video_profile": ''' + str(video_profile) + ''',
      "mic_volume": 63,
      "speaker_volume": 96,
      "chime_level": ''' + str(outdoor_chime) + ''',
      "motion_threshold": ''' + str(motion_threshold) + ''',
      "low_lux_threshold": 50,
      "med_lux_threshold": 150,
      "high_lux_threshold": 400,
      "low_front_led_dac": 220,
      "med_front_led_dac": 195,
      "high_front_led_dac": 170,
      "green_r": ''' + str(led_rgb[0]) + ''',
      "green_g": ''' + str(led_rgb[1]) + ''',
      "green_b": ''' + str(led_rgb[2]) + ''',
      "led_intensity": ''' + str(led_intensity) + ''',
      "motion_policy": "''' + motion_policy + '''"
    }'''
