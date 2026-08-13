from micropython import const
import time
import network
import ujson as json
from libraries.utils.menutools import MenuTools
from libraries.config import Config
from states.keyboard import Keyboard

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

_MAX_DISPLAY_LIST = const(3)
_DISPLAY_WIDTH = const(128)
_LIST_AREA_HEIGHT = const(54)
_ROW_HEIGHT = const(18)
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
        self.display_locs = (
            (0, 0),
            (0, 18),
            (0, 36),
        )

    def enter_state(self):
        self.app.display.oled.fill(0)
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

                # Ignore duplicate SSIDs and retain the first scan result.
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
        oled = self.app.display.oled

        for x, y in self.display_locs:
            oled.hline(x, y, _DISPLAY_WIDTH, 1)
            oled.hline(x, y + _ROW_HEIGHT - 1, _DISPLAY_WIDTH, 1)
            oled.vline(x, y, _ROW_HEIGHT, 1)
            oled.vline(_DISPLAY_WIDTH - 1, y, _ROW_HEIGHT, 1)

    def _menu(self):
        selected = self.menu_index if self.menu_flag & _MENU_SELECTED else None
        self.menu_tools._draw_selected(selected, "enter", "back")

    def _draw_network_list(self):
        oled = self.app.display.oled
        oled.fill_rect(0, 0, _DISPLAY_WIDTH, _LIST_AREA_HEIGHT, 0)

        if not self.networks:
            oled.text("No networks", 8, 17, 1)
            oled.text("found", 8, 27, 1)
            self.networks.append(("Go, back", "X", "X"))
            self._draw_borders()
            return

        first = 0 if self.current_index is None else self.current_index
        visible_count = min(self.list_max_display, len(self.networks))

        for row_index in range(self.list_max_display):
            box_x, box_y = self.display_locs[row_index]

            if row_index >= visible_count:
                continue

            network_index = (first + row_index) % len(self.networks)
            ssid, rssi, security = self.networks[network_index]

            is_selected = (
                row_index == 0 and bool(self.main_flag & _MAIN_SELECTED)
            )
            background = 1 if is_selected else 0
            text_color = 0 if is_selected else 1

            oled.fill_rect(
                box_x + 1,
                box_y + 1,
                _DISPLAY_WIDTH - 2,
                _ROW_HEIGHT - 2,
                background,
            )

            ssid_text = str(ssid)[:15]
            details_text = (str(rssi) + "dBm S" + str(security))[:15]

            oled.text(ssid_text, box_x + 2, box_y + 1, text_color)
            oled.text(details_text, box_x + 2, box_y + 9, text_color)

        self._draw_borders()

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

        self._show_queue()
        self.dirty = 0

    def _show_queue(self):
        oled = self.app.display.oled

        try:
            oled.show()
        except OSError:
            time.sleep_ms(5)
            oled.show()
            
    def exit_state(self):
        return
    
    
"""
Intermediate between keyboard and WifiState
TODO: include graphics i.e animations ect
faulty password vs fatal error handling
hidden netework proper handler
clean up for memory in the heap
"""
    

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
        self.app.display.oled.fill(0)
        self.app.display.oled.text("Connecting...", 1, 10, 1)
        self.app.display.oled.text(self.ssid_, 1, 20, 1)
        self.app.display.oled.show()
    
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
            self.app.display.oled.fill(0)
            self.app.display.oled.text("ERROR OCCURED", 1, 10, 1)
            self.app.display.oled.text(connectionError, 1, 30, 1)
            self.app.display.oled.show()
            time.sleep(3)
        
            
            try:
                self.station.connect(WIFI_SSID, WIFI_PASSWORD) # TODO: make config load from ini in boot
                
                
            except Exception as FatalConnErr:
                self.app.display.oled.fill(0)
                self.app.display.oled.text("cant connect w saved creds..")
                self.app.display.show()
                time.sleep(5)
                
        
        else:
            self.app.display.oled.fill_rect(1, 10, 124, 20, 0)
            self.app.display.oled.text("Connected!", 1, 10, 1)
            self.app.display.oled.text("Saving...", 1, 20, 1)
            self.app.display.oled.show()
            
            
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


