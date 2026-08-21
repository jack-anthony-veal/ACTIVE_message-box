from config import WIFI_SSID, WIFI_PASSWORD, DIAL_EVENT, BUTTON_PRESS as BUTTON_EVENT
from config.ui_config import (
    COLOR_ERROR, COLOR_SUCCESS, COLOR_TEXT,
    CONTENT_BOTTOM, SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X,
    STATE_ART_Y, STATE_TEXT_Y,
)
from libraries.config import Config
from micropython import const
from states.settings.wifi_settings import WifiSettings
import network
import time


_CONNECTED = const(1)
_NOT_CONNECTED = const(2)
_CHANGE = const(1)
_BACK = const(2)
_REFRESH = const(4)
_MENU = const(8)
_NONE_FLAG = const(1)


class WifiState:
    def __init__(self, app):
        config_reader = Config()
        stats = config_reader.read("./config/network.ini")
        self._PASS = str(stats["login"]["pass"])
        self._SSID = str(stats["login"]["ssid"])
        del config_reader
        self.app = app
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.connected_flag = 0
        self.connection_info = {"SSID": None, "Status": None}
        self.options_x_flag = _NONE_FLAG
        self.current_index = None
        self.dirty = _REFRESH | _MENU
        self.options = ["change", "back"]

    def _connect_sequence(self):
        try:
            station = self.station
            station.active(False)
            time.sleep_ms(20)
            station.active(True)
            station.disconnect()
            time.sleep_ms(20)
            station.connect(self._SSID, self._PASS)
            timeout = 5
            while not station.isconnected() and timeout > 0:
                timeout -= 1
                time.sleep_ms(1000)
            if station.isconnected():
                print("connected")
                return True
            return False
        except OSError:
            return False

    def _draw_status(self):
        display = self.app.display
        status = str(self.connection_info["Status"])
        connected = status == "Connected"
        status_label = "Online" if connected else "Offline"
        status_asset = "status_wifi_4" if connected else "status_wifi_error"
        state_asset = "state_wifi_success" if connected else "state_wifi_error"
        if status == "Checking":
            status_label = "Checking"
            status_asset = "status_sync"
            state_asset = None
        display.begin_screen("Wi-Fi", status_label, status_asset)
        if state_asset:
            display.draw_asset(state_asset, STATE_ART_X, STATE_ART_Y)
        status_color = COLOR_TEXT
        if status == "Connected":
            status_color = COLOR_SUCCESS
        elif status == "Not Connected":
            status_color = COLOR_ERROR
        display.draw_text_block(
            "Network: " + str(self.connection_info["SSID"]),
            SCREEN_MARGIN,
            STATE_TEXT_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=status_color,
            bottom=CONTENT_BOTTOM,
        )

    def _draw_selected(self):
        selected = None
        if self.current_index == 0:
            selected = 2
        elif self.current_index == 1:
            selected = 0
        self.app.display.draw_nav_bar(
            left="Back", right="Change", selected=selected,
            left_icon="nav_back", right_icon="nav_change_edit",
        )

    def enter_state(self):
        self.connected_flag = 0
        self.connection_info["SSID"] = self._SSID
        self.connection_info["Status"] = "Checking"
        self.dirty |= _REFRESH | _MENU
        self.draw()

        if self._connect_sequence():
            self.connected_flag |= _CONNECTED
        else:
            self.connected_flag |= _NOT_CONNECTED
        self.connection_info["Status"] = (
            "Connected" if self.connected_flag & _CONNECTED else "Not Connected"
        )
        self.dirty |= _REFRESH | _MENU
        self.draw()

    def update(self):
        return

    def handle_input(self, event, type_):
        if type_ == DIAL_EVENT and self.current_index is not None:
            self.current_index = (self.current_index + event) % len(self.options)
            self.dirty |= _MENU
            return
        if type_ == BUTTON_EVENT and self.current_index is None:
            self.current_index = 0
            self.dirty |= _MENU
            return
        if type_ == BUTTON_EVENT and self.current_index is not None:
            if self.current_index == 0:
                self.app.state_manager.replace_state(WifiSettings(self.app))
            else:
                self.app.state_manager.pop_state()

    def draw(self):
        if self.dirty == 0:
            return
        self._draw_status()
        self._draw_selected()
        self.dirty = 0

    def exit_state(self):
        return
