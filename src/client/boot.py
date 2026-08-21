import gc
import sys
import time
import esp
import network
import esp32
from config.config import *
from start_up.tests import *
from hardware_devices.input_device import OnSwitch

switch = OnSwitch()
wake_pins = switch.wake_up_pins
del switch

# Trigger level: WAKEUP_ALL_LOW wakes up if ANY pin in the tuple drops to LOW
sys.path.append('config')
print(str(get_reset_reason()))
gc.collect()


def wifi_stats():
    station = network.WLAN(network.STA_IF)
    if station.isconnected():
        return True
    else: return False


def connect_wifi():
    gc.collect()
    esp.osdebug(None)
    station = network.WLAN(network.STA_IF)  # Create a net status class
    station.active(False)
    time.sleep_ms(20)
    station.active(True)
    station.disconnect()
    time.sleep_ms(20)

    try:
        station.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as error:
        print(error)
    timeout = 20

    while not station.isconnected() and timeout > 0:
        timeout -= 1
        time.sleep_ms(500)

    if station.isconnected():
        print("connected")
    else:
        return


#connect_wifi()
