import network
import esp
import gc
import time

import sys
from machine import Pin

from config.config import WIFI_PASSWORD, WIFI_SSID

sys.path.append('config')


# TODO: clean this up its a mess


# Device Handler
led = Pin(2, Pin.OUT)


def wifi_stats(station):
    return [station.isconnected()]


def connect_wifi():
    gc.collect()
    esp.osdebug(None)
    station = network.WLAN(network.STA_IF)  # Create a net status class
    station.active(False)
    time.sleep_ms(20)
    station.active(True)
    station.disconnect()
    time.sleep_ms(20)

    networks = station.scan()

    for closest_network_num, network_info in enumerate(networks):
        ssid = network_info[0].decode()
        channel = network_info[2]
        signal = network_info[3]
        security = network_info[4]
        hidden = network_info[5]

        print(f'{ssid}, channel:, {channel}, signal:, {signal}, security:, {security}, hidden:, {hidden}')

    try:
        station.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as error:
        print(error)
        led.value(0)

    timeout = 20

    while not station.isconnected() and timeout > 0:
        timeout -= 1
        time.sleep_ms(500)

    if station.isconnected():
        print("connected")
        led.value(1)
    else:
        print("retrying")

while not network.WLAN(network.STA_IF).isconnected():
    connect_wifi()
