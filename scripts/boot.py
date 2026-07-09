import network
import esp
import gc
import time
from machine import Pin

from config import WIFI_PASSWORD, WIFI_SSID, OLED_TEXT_HEIGHT, BOOT_DISPLAY_LAYOUT, BOOT_MESSAGE
from display_device import OledDisplay as display_device
from menu_handler import MenuHandler

# Device Handler
led = Pin(2, Pin.OUT)


def wifi_stats(station):
    return [station.isconnected()]


def connect_wifi():
    gc.collect()
    esp.osdebug(None)

    station = network.WLAN(network.STA_IF)  # Create a net status class
    station.active(False)
    time.sleep(1)
    station.active(True)
    station.disconnect()
    time.sleep(1)

    display = display_device()
    menu = MenuHandler()
    display.power_on()

    display.show_message("Scanning...", start_line=BOOT_DISPLAY_LAYOUT["status"], clear_screen=True)
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
        display.show_message(f'Failed CONN: {error}', start_line=BOOT_DISPLAY_LAYOUT["status"], clear_screen=True,
                             wrap=True)  # Add error handler
        led.value(0)

    timeout = 20

    while not station.isconnected() and timeout > 0:
        display.show_message(f'Connecting: {station.status()}', start_line=2, clear_screen=True)  # Add a network error
        timeout -= 1
        time.sleep_ms(200)

    if station.isconnected():
        display.show_message("Success", start_line=BOOT_DISPLAY_LAYOUT["status"],
                             clear_screen=False)  # Add a class for checking
        led.value(1)

        if_config_tup = (station.ifconfig())
        for index_of_ip, ip_address in enumerate(if_config_tup):
            if index_of_ip == 0:
                display.show_message(str(ip_address), wrap=False, clear_screen=False, start_line=4)
            elif index_of_ip == 3:
                display.show_message(str(ip_address), wrap=False, clear_screen=False, start_line=5)

        # Boot sequence
    display.clear_menu_area()  # Add a boot seq to each device?
    display.clear_message_area()
    display.show_message(BOOT_MESSAGE)
    return station


if not network.WLAN(network.STA_IF).isconnected():
    connect_wifi()
