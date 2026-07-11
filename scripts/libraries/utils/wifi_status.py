import gc
import sys
import time
from dbm import error

import esp
import network
from machine import Pin

from config.config import WIFI_PASSWORD, WIFI_SSID
def wifi_stats(station):
    return [station.isconnected()]


def reconnect():
    x = 1
    while x > 0:
        error_wifi = ""
        gc.collect()
        esp.osdebug(None)
        try:
            station = network.WLAN(network.STA_IF)  # Create a net status class
        except Exception as err:
            error_wifi = error_wifi + str(err)
            x -= 1
            break

        try:
            station.active(False)
            time.sleep_ms(20)
            station.active(True)
            station.disconnect()
            time.sleep_ms(20)

        except Exception as err:
            error_wifi = error_wifi + str(err)

        try:
            networks = station.scan()
        except Exception as err:
            error_wifi = error_wifi + str(err)
            x-=1
            break

        try:

            for closest_network_num, network_info in enumerate(networks):
                ssid = network_info[0].decode()
                channel = network_info[2]
                signal = network_info[3]
                security = network_info[4]
                hidden = network_info[5]

                print(f'{ssid}, channel:, {channel}, signal:, {signal}')

        except Exception as err:
            error_wifi = error_wifi + str(err)

        try:
            station.connect(WIFI_SSID, WIFI_PASSWORD)
        except Exception as err:
            error_wifi = error_wifi + str(err)

        timeout = 20

        while not station.isconnected() and timeout > 0:
            timeout -= 1
            time.sleep_ms(1000)

        if station.isconnected():
            print("connected")
            if error_wifi == "":
                return True, None
            else:
                return True, error_wifi
                x+=1
                break

        else:
            print("retry")
            if error_wifi == "":
                x-=1

                return False, error_wifi

            else:

                return False, None


