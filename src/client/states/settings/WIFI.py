import network
from micropython import const

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS as BUTTON_EVENT, COLOR_ERROR, COLOR_SUCCESS, COLOR_TEXT,
    CONTENT_BOTTOM, DIAL_EVENT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX,
    NETWORK_CONFIG_FILE, SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X,
    STATE_ART_Y, STATE_TEXT_Y, WIFI_CONNECT_TIMEOUT_S,
)
from libraries.config import Config
from libraries.utils.wifi import connect
from states.settings.wifi_settings import WifiSettings
from states.proc.two_mode import TwoModeController


_CONNECTED = const(1)
_NOT_CONNECTED = const(2)
_REFRESH = const(4)
_ACTION_CHANGE = const(0)
_ACTION_BACK = const(1)


class WifiState:
    def __init__(self, app):
        try:
            saved_network = Config.read(NETWORK_CONFIG_FILE)["login"]
            self._pass = str(saved_network["pass"])
            self._ssid = str(saved_network["ssid"])
        except (OSError, KeyError, TypeError):
            self._pass = ""
            self._ssid = ""
        self.app = app
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.connected_flag = 0
        self.connection_info = {"SSID": None, "Status": None}
        self.controller = TwoModeController(2)
        self.dirty = _REFRESH
        self.options = ("Change", "Back")

    def _connect_sequence(self):
        try:
            return connect(
                self.station,
                self._ssid,
                self._pass,
                WIFI_CONNECT_TIMEOUT_S,
            )
        except OSError:
            return False

    def _draw_status(self):
        display = self.app.display
        status = str(self.connection_info["Status"])
        connected = status == "Connected"
        status_label = "Online" if connected else "Offline"
        status_asset = (
            ICONS["status"]["wifi_4"]
            if connected
            else ICONS["status"]["wifi_error"]
        )
        state_asset = (
            ICONS["state"]["wifi_success"]
            if connected
            else ICONS["state"]["wifi_error"]
        )
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
        if not self.controller.menu_open:
            self.app.display.draw_nav_bar()
            return
        if self.controller.action_index == _ACTION_CHANGE:
            selected = NAV_RIGHT_INDEX
        elif self.controller.action_index == _ACTION_BACK:
            selected = NAV_LEFT_INDEX
        self.app.display.draw_nav_bar(
            left="Back", right="Change", selected=selected,
            left_icon=ICONS["navigation"]["back"],
            right_icon=ICONS["navigation"]["edit"],
        )

    def enter_state(self):
        self.connected_flag = 0
        self.controller.hide_menu()
        self.connection_info["SSID"] = self._ssid
        self.connection_info["Status"] = "Checking"
        self.dirty |= _REFRESH
        self.draw()

        if self._connect_sequence():
            self.connected_flag |= _CONNECTED
        else:
            self.connected_flag |= _NOT_CONNECTED
        self.connection_info["Status"] = (
            "Connected" if self.connected_flag & _CONNECTED else "Not Connected"
        )
        self.dirty |= _REFRESH
        self.draw()

    def update(self):
        return

    def handle_input(self, event, type_):
        if type_ == DIAL_EVENT and self.controller.rotate(event):
            self.dirty |= _REFRESH
            return
        if type_ == BUTTON_EVENT:
            selected = self.controller.activate()
            self.dirty |= _REFRESH
            if selected is None:
                print("MENU|wifi|open")
            elif selected == _ACTION_CHANGE:
                self.app.state_manager.push_state(WifiSettings(self.app))
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
