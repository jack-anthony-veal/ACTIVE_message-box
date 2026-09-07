import time

from config.config import (
    MILLISECONDS_PER_SECOND, WIFI_CONNECT_POLL_INTERVAL_MS,
    WIFI_INTERFACE_RESET_DELAY_MS,
    WIFI_RSSI_FOUR_BARS, WIFI_RSSI_ONE_BAR, WIFI_RSSI_THREE_BARS,
    WIFI_RSSI_TWO_BARS, WIFI_RSSI_UNKNOWN,
)


def reset_interface(station):
    station.active(False)
    time.sleep_ms(WIFI_INTERFACE_RESET_DELAY_MS)
    station.active(True)
    station.disconnect()
    time.sleep_ms(WIFI_INTERFACE_RESET_DELAY_MS)


def wait_for_connection(station, timeout_s):
    remaining_ms = int(timeout_s * MILLISECONDS_PER_SECOND)
    while not station.isconnected() and remaining_ms > 0:
        time.sleep_ms(WIFI_CONNECT_POLL_INTERVAL_MS)
        remaining_ms -= WIFI_CONNECT_POLL_INTERVAL_MS
    return station.isconnected()


def connect(station, ssid, password, timeout_s):
    reset_interface(station)
    station.connect(ssid, password)
    return wait_for_connection(station, timeout_s)


def signal_level(rssi):
    try:
        rssi_value = int(rssi)
    except Exception:
        rssi_value = WIFI_RSSI_UNKNOWN

    if rssi_value >= WIFI_RSSI_FOUR_BARS:
        return rssi_value, 4
    if rssi_value >= WIFI_RSSI_THREE_BARS:
        return rssi_value, 3
    if rssi_value >= WIFI_RSSI_TWO_BARS:
        return rssi_value, 2
    if rssi_value >= WIFI_RSSI_ONE_BAR:
        return rssi_value, 1
    return rssi_value, 0
