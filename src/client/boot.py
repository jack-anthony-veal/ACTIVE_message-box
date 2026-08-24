import gc
import network

from config.config import (
    WIFI_BOOT_CONNECT_TIMEOUT_S, WIFI_PASSWORD, WIFI_SSID,
)
from hardware_devices.input_device import OnSwitch
from libraries.utils.wifi import connect
from start_up.tests import get_reset_reason


wake_pins = OnSwitch().wake_up_pins


def wifi_stats():
    return network.WLAN(network.STA_IF).isconnected()


def connect_wifi():
    try:
        import esp

        esp.osdebug(None)
    except (ImportError, AttributeError):
        pass

    station = network.WLAN(network.STA_IF)
    try:
        connected = connect(
            station,
            WIFI_SSID,
            WIFI_PASSWORD,
            WIFI_BOOT_CONNECT_TIMEOUT_S,
        )
    except OSError as error:
        print("Wi-Fi connection error:", error)
        return False

    if connected:
        print("connected")
    return connected


print(str(get_reset_reason()))
gc.collect()
