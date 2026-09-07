import gc

from app.ota_boot import begin


begin()

try:
    from hardware_devices.input_device import OnSwitch

    wake_pins = OnSwitch().wake_up_pins
except Exception as error:
    wake_pins = []
    print("WARNING|wake_input|{}".format(error))


def wifi_stats():
    import network

    return network.WLAN(network.STA_IF).isconnected()


def connect_wifi():
    import network

    from config.config import (
        WIFI_BOOT_CONNECT_TIMEOUT_S, WIFI_PASSWORD, WIFI_SSID,
    )
    from libraries.utils.wifi import connect

    try:
        import esp

        esp.osdebug(None)
    except (ImportError, AttributeError):
        pass
    station = network.WLAN(network.STA_IF)
    try:
        connected = connect(
            station, WIFI_SSID, WIFI_PASSWORD, WIFI_BOOT_CONNECT_TIMEOUT_S
        )
    except OSError as error:
        print("WARNING|wifi_connect|{}".format(error))
        return False
    if connected:
        print("WIFI|connected")
    return connected


try:
    from start_up.tests import get_reset_reason

    print(str(get_reset_reason()))
except Exception as error:
    print("WARNING|reset_reason|{}".format(error))

try:
    connect_wifi()
except Exception as error:
    print("WARNING|wifi_boot|{}".format(error))
gc.collect()
