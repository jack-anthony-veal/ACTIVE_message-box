from micropython import const
import time
import network
import ujson as json
from libraries.utils.menutools import MenuTools
from libraries.config import Config
from states.keyboard import Keyboard
from config.ui_config import (
    COLOR_ERROR, COLOR_SUCCESS, CONTENT_BOTTOM, CONTENT_TOP,
    SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X, STATE_ART_Y, STATE_TEXT_Y,
)

try:
    import config.config as _config
except ImportError:
    import config as _config

DIAL_EVENT = _config.DIAL_EVENT
BUTTON_EVENT = _config.BUTTON_PRESS
WIFI_SSID = getattr(_config, "WIFI_SSID", "")
WIFI_PASSWORD = getattr(
    _config,
    "WIFI_PASSWORD",
    getattr(_config, "WIFI_PASS", ""),
)

_LIST_DIRTY = const(1 << 0)
_MENU_DIRTY = const(1 << 1)

_MAIN_SELECTED = const(1 << 0)
_MENU_SELECTED = const(1 << 1)

_MAX_DISPLAY_LIST = const(5)
import os

class WifiSettings:
    def __init__(self, app):
        self.return_kb_buffer = bytearray()
        self.selected_ssid_buffer = bytearray()
        
        self.app = app

        self.station = network.WLAN(network.STA_IF)
        self.saved_ssid = WIFI_SSID
        self.saved_pass = WIFI_PASSWORD
        
        self.networks = []
        self.list_max_display = _MAX_DISPLAY_LIST

        self.current_index = None
        self.menu_index = None

        self.main_flag = _MAIN_SELECTED
        self.menu_flag = 0
        self.dirty = _LIST_DIRTY | _MENU_DIRTY

        self.menu_tools = MenuTools(self.app)
    def enter_state(self):
        self.app.display.begin_screen(
            "Wi-Fi networks", "Scanning", ("status_wifi_0", "status_sync")
        )
        errors = []
        station = self.station
        station.active(False)
        time.sleep_ms(20)
        station.active(True)
        station.disconnect()
        time.sleep_ms(20)
        scanned_networks = ()

        try:
            scanned_networks = station.scan()
        except Exception as err:
            errors.append("scan: " + str(err))

        self.networks = []
        seen_ssids = set()

        for network_info in scanned_networks:
            try:
                raw_ssid = network_info[0]
                try:
                    ssid = raw_ssid.decode()
                except Exception:
                    ssid = str(raw_ssid)

                if not ssid:
                    ssid = "<hidden>"

                if ssid in seen_ssids:
                    continue

                seen_ssids.add(ssid)
                rssi = int(network_info[3])
                security = int(network_info[4])
                self.networks.append((ssid, rssi, security))

            except (IndexError, TypeError, ValueError) as err:
                errors.append("network entry: " + str(err))

        self.networks.sort(key=lambda item: item[1], reverse=True)

        self.current_index = 0 if self.networks else None
        self.menu_index = None
        self.main_flag = _MAIN_SELECTED
        self.menu_flag = 0
        self.dirty = _LIST_DIRTY | _MENU_DIRTY

        if errors:
            print("Wi-Fi scan warnings: " + " | ".join(errors))

        self.draw()

    def _draw_borders(self):
        return

    def _menu(self):
        selected = self.menu_index if self.menu_flag & _MENU_SELECTED else None
        self.menu_tools._draw_selected(selected, "enter", "back")

    def _draw_network_list(self):
        display = self.app.display
        display.begin_screen("Wi-Fi networks", "Rotate")

        if not self.networks:
            display.draw_text_block(
                "No networks found",
                SCREEN_MARGIN,
                CONTENT_TOP + 32,
                SCREEN_WIDTH - SCREEN_MARGIN * 2,
                bottom=CONTENT_BOTTOM,
            )
            self.networks.append(("Go, back", "X", "X"))
            return

        first = 0 if self.current_index is None else self.current_index
        visible_count = min(self.list_max_display, len(self.networks))

        for row_index in range(self.list_max_display):
            if row_index >= visible_count:
                continue

            network_index = (first + row_index) % len(self.networks)
            ssid, rssi, security = self.networks[network_index]

            is_selected = (
                row_index == 0 and bool(self.main_flag & _MAIN_SELECTED)
            )
            display.draw_wifi_row(
                row_index, str(ssid), rssi, security, selected=is_selected
            )

    def _select_current_network(self):
        if self.current_index is None or not self.networks:
            return

        ssid, rssi, security = self.networks[self.current_index]
        self.saved_ssid = ssid

        callback = getattr(self.app, "on_wifi_network_selected", None)
        if callback is not None:
            callback(ssid, rssi, security)
        else:
            print("Selected Wi-Fi: " + ssid)
            txt = map(ord, ssid)                
            self.selected_ssid_buffer.extend(txt)
            return

    def _go_back(self):
        callback = getattr(self.app, "on_wifi_back", None)
        if callback is not None:
            callback()
        else:
            print("Back selected")

    def update(self):
        return

    def handle_input(self, event, type_):
        if type_ is None or event is None:
            return

        if type_ == DIAL_EVENT:
            if self.main_flag & _MAIN_SELECTED:
                if not self.networks:
                    return

                current = 0 if self.current_index is None else self.current_index
                self.current_index = (current + event) % len(self.networks)
                self.dirty |= _LIST_DIRTY

            elif self.menu_flag & _MENU_SELECTED:
                current = 0 if self.menu_index is None else self.menu_index
                self.menu_index = (current + event) % 2
                self.dirty |= _MENU_DIRTY
                

            self.draw()
            return

        if type_ != BUTTON_EVENT:
            return

        if self.main_flag & _MAIN_SELECTED:
            if not self.networks:
                return

            self.main_flag = 0
            self.menu_flag = _MENU_SELECTED
            self.menu_index = 0
            self.dirty |= _LIST_DIRTY | _MENU_DIRTY
            self.draw()
            return

        if self.menu_flag & _MENU_SELECTED:
            selected = 0 if self.menu_index is None else self.menu_index

            self.menu_flag = 0
            self.main_flag = _MAIN_SELECTED
            self.menu_index = None
            self.dirty |= _LIST_DIRTY | _MENU_DIRTY
            self.draw()

            if selected == 0:
                self._select_current_network()
                self.connecting = Connecting(self.app, self.return_kb_buffer, self.selected_ssid_buffer)
                self.app.state_manager.replace_state(Keyboard(self.app, self.connecting, self.return_kb_buffer, self.saved_ssid))
                return
                
            else:
                self.app.state_manager.pop_state()
                return

    def draw(self):
        if self.dirty == 0:
            return

        if self.dirty & _LIST_DIRTY:
            self._draw_network_list()

        if self.dirty & _MENU_DIRTY:
            self._menu()

        self.dirty = 0
            
    def exit_state(self):
        return
    
    
class Connecting:
    def __init__(self, app, return_buf, ssid_buf):
        self.app = app
        self.pass_buf = return_buf
        self.ssid_buf = ssid_buf
        self.station = network.WLAN(network.STA_IF)
        self.config_func = Config()
        self.pass_ = ""
        self.ssid_ = ""
        
    def enter_state(self):
        self.pass_ =self.pass_buf.decode('utf-8')
        self.ssid_ = self.ssid_buf.decode('utf-8')
        print(self.pass_ + self.ssid_)
        self.draw()
        
    def update(self):
        return
    
    def draw(self):
        display = self.app.display
        display.begin_screen("Connecting", "Wi-Fi", "status_sync")
        display.draw_text_block(
            self.ssid_, SCREEN_MARGIN, CONTENT_TOP + 40,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
        )
    
        self.station.active(False)
        time.sleep_ms(20)
        self.station.active(True)
        self.station.disconnect()
        time.sleep_ms(20)
        self.station.connect(self.ssid_, self.pass_)
        timeout = 10
        
        while not self.station.isconnected() and timeout > 0:
            timeout -= 1
            time.sleep_ms(1000)

        if not self.station.isconnected():
            connectionError = "Cant connect to hidden nets" if self.ssid_.lower() == "<hidden>" else "couldnt connect"
            display.begin_screen("Connection failed", "Error", "status_wifi_error")
            display.draw_asset("state_wifi_error", STATE_ART_X, STATE_ART_Y)
            display.draw_text_block(
                connectionError, SCREEN_MARGIN, STATE_TEXT_Y,
                SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_ERROR,
            )
            time.sleep(3)
            try:
                self.station.connect(WIFI_SSID, WIFI_PASSWORD) # TODO: make config load from ini in boot
                
                
            except Exception as FatalConnErr:
                display.begin_screen("Connection failed", "Error")
                display.draw_text_block(
                    "Cannot reconnect with saved credentials",
                    SCREEN_MARGIN,
                    CONTENT_TOP + 32,
                    SCREEN_WIDTH - SCREEN_MARGIN * 2,
                    color=COLOR_ERROR,
                )
                time.sleep(5)
                
        
        else:
            display.begin_screen("Connected", "Wi-Fi", "status_wifi_4")
            display.draw_asset("state_wifi_success", STATE_ART_X, STATE_ART_Y)
            display.draw_text_block(
                "Saving network settings",
                SCREEN_MARGIN,
                STATE_TEXT_Y,
                SCREEN_WIDTH - SCREEN_MARGIN * 2,
                color=COLOR_SUCCESS,
            )
            
            
            self.ssid_ = self.config_func.format(self.ssid_)
            self.pass_ = self.config_func.format(self.pass_)
            data = {"login":{"ssid": self.ssid_, "pass": self.pass_}}
            self.config_func.write("./config/network.ini", data)
            
            
            check_data = self.config_func.read("./config/network.ini")
            print(str(check_data))
            time.sleep(5)
            
        self.app.state_manager.replace_state(WifiSettings(self.app))
                                             
    def handle_input(self):
        return
    def exit_state(self):
        return
