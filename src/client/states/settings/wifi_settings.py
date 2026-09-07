import time

import network
from micropython import const

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS as BUTTON_EVENT, COLOR_ERROR, COLOR_SUCCESS, CONTENT_BOTTOM,
    CONTENT_TOP, DIAL_EVENT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX,
    NETWORK_CONFIG_FILE, SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X,
    STATE_ART_Y, STATE_TEXT_FALLBACK_OFFSET_Y, STATE_TEXT_Y,
    WIFI_CONNECT_TIMEOUT_S, WIFI_FAILURE_DISPLAY_MS, WIFI_NEW_NETWORK_TIMEOUT_S,
    WIFI_PASSWORD, WIFI_RESULT_DISPLAY_MS, WIFI_SCAN_RSSI_INDEX,
    WIFI_SCAN_SECURITY_INDEX, WIFI_SCAN_SSID_INDEX, WIFI_SSID,
    WIFI_VISIBLE_ROWS,
)
from libraries.config import Config
from libraries.utils.wifi import connect, reset_interface, signal_level
from states.keyboard import Keyboard
from states.proc.two_mode import TwoModeController


_LIST_DIRTY = const(1 << 0)
_MENU_DIRTY = const(1 << 1)
_ACTION_ENTER = const(0)
_ACTION_BACK = const(1)


class WifiSettings:
    def __init__(self, app):
        self.app = app
        self.station = network.WLAN(network.STA_IF)
        self.saved_ssid = WIFI_SSID

        self.return_kb_buffer = bytearray()
        self.selected_ssid_buffer = bytearray()
        self.networks = []

        self.current_index = None
        self.controller = TwoModeController(2)
        self.dirty = _LIST_DIRTY | _MENU_DIRTY

        self.actions = ("Enter", "Back")
        self.action_icons = (
            ICONS["navigation"]["select"],
            ICONS["navigation"]["back"],
        )

    def enter_state(self):
        self.app.display.begin_screen(
            "Wi-Fi networks",
            "Scanning",
            (ICONS["status"]["wifi_0"], ICONS["status"]["sync"]),
        )
        errors = []
        try:
            reset_interface(self.station)
            scanned_networks = self.station.scan()
        except Exception as error:
            scanned_networks = ()
            errors.append("scan: " + str(error))

        self.networks = self._normalise_networks(scanned_networks, errors)
        self.current_index = 0 if self.networks else None
        self.controller.hide_menu()
        self.dirty = _LIST_DIRTY | _MENU_DIRTY

        if errors:
            print("Wi-Fi scan warnings: " + " | ".join(errors))
        self.draw()

    @staticmethod
    def _normalise_networks(scanned_networks, errors):
        networks = []
        seen_ssids = set()
        for network_info in scanned_networks:
            try:
                raw_ssid = network_info[WIFI_SCAN_SSID_INDEX]
                try:
                    ssid = raw_ssid.decode()
                except Exception:
                    ssid = str(raw_ssid)
                if not ssid:
                    ssid = "<hidden>"
                if ssid in seen_ssids:
                    continue
                seen_ssids.add(ssid)
                networks.append((
                    ssid,
                    int(network_info[WIFI_SCAN_RSSI_INDEX]),
                    int(network_info[WIFI_SCAN_SECURITY_INDEX]),
                ))
            except (IndexError, TypeError, ValueError) as error:
                errors.append("network entry: " + str(error))
        networks.sort(key=lambda item: item[1], reverse=True)
        return networks

    def _draw_actions(self):
        if not self.controller.menu_open:
            self.app.display.draw_nav_bar()
            return
        selected = (
            NAV_RIGHT_INDEX
            if self.controller.action_index == _ACTION_ENTER
            else NAV_LEFT_INDEX
        )
        self.app.display.draw_nav_bar(
            left=self.actions[_ACTION_BACK],
            right=self.actions[_ACTION_ENTER],
            selected=selected,
            left_icon=self.action_icons[_ACTION_BACK],
            right_icon=self.action_icons[_ACTION_ENTER],
        )

    def _draw_network_list(self):
        display = self.app.display
        display.begin_screen("Wi-Fi networks", "Rotate")

        if not self.networks:
            display.draw_text_block(
                "No networks found",
                SCREEN_MARGIN,
                CONTENT_TOP + STATE_TEXT_FALLBACK_OFFSET_Y,
                SCREEN_WIDTH - SCREEN_MARGIN * 2,
                bottom=CONTENT_BOTTOM,
            )
            return

        first = 0 if self.current_index is None else self.current_index
        visible_count = min(WIFI_VISIBLE_ROWS, len(self.networks))
        for row_index in range(visible_count):
            network_index = (first + row_index) % len(self.networks)
            ssid, rssi, security = self.networks[network_index]
            rssi_value, bars = signal_level(rssi)
            display.draw_list_row(
                row_index,
                str(ssid),
                subtitle="secured" if security else "open",
                selected=(
                    row_index == 0 and not self.controller.menu_open
                ),
                icon=ICONS["status"]["wifi_" + str(bars)],
                secondary_icon=(
                    ICONS["status"]["lock"]
                    if str(ssid) == "<hidden>" or security
                    else None
                ),
                trailing_text=str(rssi_value),
            )

    def _select_current_network(self):
        if self.current_index is None or not self.networks:
            return False

        ssid, rssi, security = self.networks[self.current_index]
        self.saved_ssid = ssid
        callback = getattr(self.app, "on_wifi_network_selected", None)
        if callback is not None:
            callback(ssid, rssi, security)
        else:
            del self.selected_ssid_buffer[:]
            self.selected_ssid_buffer.extend(ssid.encode("utf-8"))
        return True

    def update(self):
        return

    def handle_input(self, event, event_type):
        if event_type is None or event is None:
            return

        if event_type == DIAL_EVENT:
            if not self.controller.menu_open:
                if not self.networks:
                    return
                current = 0 if self.current_index is None else self.current_index
                self.current_index = (current + event) % len(self.networks)
                self.dirty |= _LIST_DIRTY
            else:
                self.controller.rotate(event)
                self.dirty |= _MENU_DIRTY
            self.draw()
            return

        if event_type != BUTTON_EVENT:
            return

        if not self.controller.menu_open:
            self.controller.show_menu(
                _ACTION_ENTER if self.networks else _ACTION_BACK
            )
            self.dirty |= _LIST_DIRTY | _MENU_DIRTY
            self.draw()
            return

        if self.controller.menu_open:
            selected = self.controller.activate()
            self.dirty |= _LIST_DIRTY | _MENU_DIRTY
            self.draw()

            if selected == _ACTION_ENTER and self._select_current_network():
                connecting = Connecting(
                    self.app,
                    self.return_kb_buffer,
                    self.selected_ssid_buffer,
                )
                self.app.state_manager.replace_state(
                    Keyboard(
                        self.app,
                        connecting,
                        self.return_kb_buffer,
                        self.saved_ssid,
                    )
                )
            elif selected == _ACTION_BACK:
                self.app.state_manager.pop_state()

    def draw(self):
        if self.dirty == 0:
            return
        if self.dirty & _LIST_DIRTY:
            self._draw_network_list()
        if self.dirty & _MENU_DIRTY:
            self._draw_actions()
        self.dirty = 0

    def exit_state(self):
        return


class Connecting:
    def __init__(self, app, return_buf, ssid_buf):
        self.app = app
        self.pass_buf = return_buf
        self.ssid_buf = ssid_buf
        self.station = network.WLAN(network.STA_IF)
        self.password = ""
        self.ssid = ""

    def enter_state(self):
        self.password = self.pass_buf.decode("utf-8")
        self.ssid = self.ssid_buf.decode("utf-8")
        self.draw()

    def update(self):
        return

    def draw(self):
        display = self.app.display
        display.begin_screen(
            "Connecting", "Wi-Fi", ICONS["status"]["sync"]
        )
        display.draw_text_block(
            self.ssid,
            SCREEN_MARGIN,
            CONTENT_TOP + STATE_TEXT_FALLBACK_OFFSET_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
        )

        try:
            connected = connect(
                self.station,
                self.ssid,
                self.password,
                WIFI_NEW_NETWORK_TIMEOUT_S,
            )
        except OSError:
            connected = False

        if connected:
            self._show_success(display)
        else:
            self._show_failure(display)

        self.app.state_manager.replace_state(WifiSettings(self.app))

    def _show_failure(self, display):
        message = (
            "Cannot connect to hidden networks"
            if self.ssid.lower() == "<hidden>"
            else "Could not connect"
        )
        display.begin_screen(
            "Connection failed", "Error", ICONS["status"]["wifi_error"]
        )
        display.draw_asset(
            ICONS["state"]["wifi_error"], STATE_ART_X, STATE_ART_Y
        )
        display.draw_text_block(
            message,
            SCREEN_MARGIN,
            STATE_TEXT_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=COLOR_ERROR,
        )
        time.sleep_ms(WIFI_FAILURE_DISPLAY_MS)

        if WIFI_SSID:
            try:
                connect(
                    self.station,
                    WIFI_SSID,
                    WIFI_PASSWORD,
                    WIFI_CONNECT_TIMEOUT_S,
                )
            except OSError:
                display.begin_screen("Connection failed", "Error")
                display.draw_text_block(
                    "Cannot reconnect with saved credentials",
                    SCREEN_MARGIN,
                    CONTENT_TOP + STATE_TEXT_FALLBACK_OFFSET_Y,
                    SCREEN_WIDTH - SCREEN_MARGIN * 2,
                    color=COLOR_ERROR,
                )
                time.sleep_ms(WIFI_RESULT_DISPLAY_MS)

    def _show_success(self, display):
        display.begin_screen(
            "Connected", "Wi-Fi", ICONS["status"]["wifi_4"]
        )
        display.draw_asset(
            ICONS["state"]["wifi_success"], STATE_ART_X, STATE_ART_Y
        )
        display.draw_text_block(
            "Saving network settings",
            SCREEN_MARGIN,
            STATE_TEXT_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=COLOR_SUCCESS,
        )
        Config.write(
            NETWORK_CONFIG_FILE,
            {"login": {"ssid": self.ssid, "pass": self.password}},
        )
        time.sleep_ms(WIFI_RESULT_DISPLAY_MS)

    def handle_input(self, event=None, event_type=None):
        return

    def exit_state(self):
        return
