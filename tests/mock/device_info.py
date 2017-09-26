"""Mock Skybell Device Info Response."""

from tests.mock.device import DEVID

SSID = 'devid123abc'
WIFI_STATUS = 'good'


def get_response_ok(dev_id=DEVID, ssid=SSID, wifi_status=WIFI_STATUS):
    """Return the successful device info response json."""
    return '''
    {
      "wifiNoise": "-79",
      "wifiBitrate": "52",
      "proxy_port": "5683",
      "wifiLinkQuality": "92",
      "port": "5683",
      "wifiSnr": "29",
      "mac": "dd:cc:99:00:77:88",
      "serialNo": "333444555666",
      "wifiTxPwrEeprom": "16",
      "hardwareRevision": "SKYBELL_HD_3_1_1008848-009",
      "proxy_address": "127.0.0.1",
      "localHostname": "host.internal",
      "address": "127.0.0.1",
      "firmwareVersion": "1128",
      "essid": "''' + ssid + '''",
      "timestamp": "63673679013",
      "wifiSignalLevel": "-50",
      "deviceId": "''' + dev_id + '''",
      "checkedInAt": "2017-09-26T21:03:33.000Z",
      "status": {
        "wifiLink": "''' + wifi_status + '''"
      }
    }'''
