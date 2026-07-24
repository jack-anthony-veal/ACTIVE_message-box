# IN DEVELOPMENT

from states.wifi_settings import WifiSettings

from micropython import const
import time
import network
from config import (WIFI_SSID, WIFI_PASSWORD, DIAL_EVENT, BUTTON_PRESS as BUTTON_EVENT)

_CONNECTED = const(1)
_NOT_CONNECTED = const(2)
_SSID = WIFI_SSID
_PASS = WIFI_PASSWORD
_CHANGE = const(1)
_BACK = const(2)
_REFRESH = const(4)

_WIFI_FACE_X = const(8)
_WIFI_FACE_Y = const(15)

_WIFI_FACE_WIDTH = const(49)
_WIFI_FACE_HEIGHT = const(33)

_WIFI_FACE = (
    b"\x00\x12\x0c"

    b"\x01\x0f\x13"
    b"\x02\x0f\x13"

    b"\x03\x0d\x16"
    b"\x04\x0d\x16"

    b"\x05\x0b\x20"
    b"\x06\x0b\x20"

    b"\x07\x03\x1b"
    b"\x07\x2b\x02"

    b"\x08\x03\x1b"
    b"\x08\x2b\x02"

    b"\x09\x01\x1b"
    b"\x09\x2d\x02"

    b"\x0a\x01\x1b"
    b"\x0a\x2d\x02"

    b"\x0b\x00\x03"
    b"\x0b\x07\x02"
    b"\x0b\x0d\x02"
    b"\x0b\x12\x02"
    b"\x0b\x18\x04"
    b"\x0b\x1e\x07"
    b"\x0b\x27\x04"
    b"\x0b\x2f\x02"

    b"\x0c\x00\x03"
    b"\x0c\x07\x02"
    b"\x0c\x0d\x02"
    b"\x0c\x12\x02"
    b"\x0c\x18\x04"
    b"\x0c\x1e\x07"
    b"\x0c\x27\x04"
    b"\x0c\x2f\x02"

    b"\x0d\x00\x05"
    b"\x0d\x07\x02"
    b"\x0d\x0d\x02"
    b"\x0d\x11\x09"
    b"\x0d\x1e\x02"
    b"\x0d\x2f\x02"

    b"\x0e\x00\x05"
    b"\x0e\x07\x02"
    b"\x0e\x0d\x02"
    b"\x0e\x11\x09"
    b"\x0e\x1e\x02"
    b"\x0e\x2f\x02"

    b"\x0f\x00\x05"
    b"\x0f\x07\x02"
    b"\x0f\x0d\x02"
    b"\x0f\x11\x03"
    b"\x0f\x18\x02"
    b"\x0f\x1e\x02"
    b"\x0f\x27\x04"
    b"\x0f\x2f\x02"

    b"\x10\x00\x14"
    b"\x10\x18\x02"
    b"\x10\x1e\x05"
    b"\x10\x27\x04"
    b"\x10\x2f\x02"

    b"\x11\x00\x05"
    b"\x11\x11\x03"
    b"\x11\x18\x02"
    b"\x11\x1e\x05"
    b"\x11\x27\x04"
    b"\x11\x2f\x02"

    b"\x12\x00\x05"
    b"\x12\x11\x03"
    b"\x12\x18\x02"
    b"\x12\x1e\x02"
    b"\x12\x27\x04"
    b"\x12\x2f\x02"

    b"\x13\x00\x05"
    b"\x13\x11\x03"
    b"\x13\x18\x02"
    b"\x13\x1e\x02"
    b"\x13\x27\x04"
    b"\x13\x2f\x02"

    b"\x14\x00\x07"
    b"\x14\x09\x04"
    b"\x14\x0f\x05"
    b"\x14\x18\x02"
    b"\x14\x1e\x02"
    b"\x14\x27\x04"
    b"\x14\x2f\x02"

    b"\x15\x00\x07"
    b"\x15\x09\x04"
    b"\x15\x0f\x05"
    b"\x15\x18\x02"
    b"\x15\x1e\x02"
    b"\x15\x27\x04"
    b"\x15\x2f\x02"

    b"\x16\x00\x18"
    b"\x16\x2d\x02"

    b"\x17\x00\x18"
    b"\x17\x2d\x02"

    b"\x18\x01\x15"
    b"\x18\x2b\x02"

    b"\x19\x01\x15"
    b"\x19\x2b\x02"

    b"\x1a\x03\x28"
    b"\x1b\x03\x28"

    b"\x1c\x0b\x18"
    b"\x1d\x0b\x18"

    b"\x1e\x0d\x15"
    b"\x1f\x0d\x15"

    b"\x20\x12\x0c"
)


_WIFI_ICON_X = const(2)
_WIFI_ICON_Y = const(2)

_WIFI_ICON_WIDTH = const(16)
_WIFI_ICON_HEIGHT = const(14)

_WIFI_ICON = (
    b"\x00\x03\x0a"

    b"\x01\x02\x0c"

    b"\x02\x01\x03"
    b"\x02\x0c\x03"

    b"\x03\x00\x03"
    b"\x03\x0e\x02"

    b"\x04\x00\x02"
    b"\x04\x06\x04"
    b"\x04\x0e\x02"

    b"\x05\x03\x0a"
    b"\x05\x0f\x01"

    b"\x06\x02\x04"
    b"\x06\x0a\x04"

    b"\x07\x02\x02"
    b"\x07\x06\x04"
    b"\x07\x0c\x02"

    b"\x08\x06\x04"

    b"\x09\x05\x02"
    b"\x09\x09\x02"

    b"\x0b\x07\x02"
    b"\x0c\x07\x02"
    b"\x0d\x07\x02"
)
_MENU = const(8)

_BACK_X = const(64)
_CHANGE_X = const(0)

_BACK_FLAG = 1 << 6
_CHANGE_FLAG = 1 << 2
_NONE_FLAG = 1

_MENU_Y_AXIS = const(54)

class WifiState:
    def __init__(self, app):
        self.app = app
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
            
        self.connected_flag = 0
        
        self.connection_info = {
            "SSID": None,
            "Status": None,
        }
        
        self.options_x_flag =_NONE_FLAG
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

            station.connect(_SSID, _PASS)
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

    def _draw_menu_opts_corners(self):
        oled = self.app.display.oled
        hline = oled.hline
        vline = oled.vline
        
        change_x = 0
        back_x = 64
        y = _MENU_Y_AXIS
        size_y = 4
        size_x = 4
        
        for point_in_space in range(y, y+12, 2):
                vline(63, point_in_space, 1, 1)
                vline(0, point_in_space, 1, 1)
                vline(127, point_in_space, 1, 1)
                
        for x in (change_x, back_x):
            for point_in_space in range(0, 129, 4):
                hline(point_in_space, y, 2, 1)
                hline(point_in_space, 63, 2, 1)
            
            
                
                        
    def _draw_selected(self):
        oled = self.app.display.oled
        
        oled.fill_rect(0, _MENU_Y_AXIS, (_BACK_FLAG*2), (_BACK_FLAG-_MENU_Y_AXIS), 0)
        
        if self.options_x_flag & _NONE_FLAG:
            oled.text(" change", 1, _MENU_Y_AXIS+1, 1)
            oled.text(" back", 65, _MENU_Y_AXIS+1, 1)
            self._draw_menu_opts_corners()
            return
        

        change_color = 0
        change_selected = 0
        change_background = 0
        
        change_selected = 1 if self.current_index == 0 else 0
        change_color = 0 if change_selected else 1
        change_background = 1 if change_selected else 0
        
        oled.fill_rect(0, _MENU_Y_AXIS, 64, 12, change_background)
        back_results = (0, 1) if change_selected else (1, 0)
        
        oled.fill_rect(64, _MENU_Y_AXIS, 64, 12, back_results[0])
        
        oled.text("change", 1, _MENU_Y_AXIS+1, change_color)
        
        oled.text("back", 65, _MENU_Y_AXIS+1, back_results[1])
        self._draw_menu_opts_corners()
    
    
    def _draw_wifi_symbol(self):
        display = self.app.display
        display.draw_art(_WIFI_ICON, _WIFI_ICON_X, _WIFI_ICON_Y)
        time.sleep_ms(2)
        display.draw_art(_WIFI_FACE, _WIFI_FACE_X, _WIFI_FACE_Y)

        
    def _draw_status(self): # TODO: Remove magic numbers
        oled = self.app.display.oled        
        ssid_ = str(self.connection_info["SSID"])
        status = str(self.connection_info["Status"])
        
        # Text wrapper for wifi info
        
        oled.fill_rect(_BACK_FLAG, 8, (_BACK_FLAG-1), 46, 0)

        for start_line, text in enumerate([ssid_, status]):
            y_axis = 24 if start_line == 1 else 8
            
            for index_, increment in enumerate(range(0, len(text), 7)):
                if increment > 13: break
                split_text = text[increment:increment+7]
                y_ = y_axis + (index_*8)
                oled.text(split_text, _BACK_FLAG + 1, y_, 1)
                
    
    def _show_queue(self):
        oled= self.app.display.oled
        try:
            oled.show()
        except OSError:
            time.sleep_ms(5)
            oled.show()
        
    def enter_state(self): # TODO: Remove duplicates
        self.app.display.oled.fill(0)
        self.connected_flag = 0
        self.connection_info["SSID"] = _SSID
        self.connection_info["Status"] = "..."
        
        self.dirty |= _REFRESH
        self.dirty |= _MENU
        
        self._draw_wifi_symbol()
        self.draw()
        
        if self._connect_sequence():
            self.connected_flag |= _CONNECTED
        else:
            self.connected_flag |= _NOT_CONNECTED
            
        status_ = "Connected" if self.connected_flag & _CONNECTED else "Not Connected"
        self.connection_info["Status"] = status_
        
        
        with open("wifistatus.tmp", "w") as temp:
            temp.write(str(self.connection_info["SSID"]) + '\n')
            temp.write(str(_PASS))
            temp.write(str(self.connection_info["Status"]) + '\n')
            temp.close()
        
        
        
        self.dirty |= _REFRESH
        self.dirty |= _MENU
        self.draw()
        
            
    def update(self):
        return
    
    def handle_input(self, event, type_):
        if type_ == DIAL_EVENT and self.current_index is not None:
            self.current_index = (self.current_index + event) % len(self.options)
            self.options_x_flag = 0
            if self.current_index == 0: self.options_x_flag |= _CHANGE_FLAG
            else: self.options_x_flag |= _BACK_FLAG
            self.dirty |= _MENU
            return
            
        if type_ == BUTTON_EVENT and self.current_index is None:
            self.current_index = 0
            self.dirty |= _MENU
            self.options_x_flag = 0
            self.options_x_flag |= _CHANGE_FLAG
            return
        
        if type_ == BUTTON_EVENT and self.current_index is not None:
            self.options_x_flag = 0
            self.options_x_flag |= _NONE_FLAG            
            if self.current_index == 0:
                self.app.state_manager.replace_state(WifiSettings(self.app))
            else:
                self.app.state_manager.pop_state()
            return
        
    def draw(self):
        if self.dirty == 0:
            return
        
        if self.dirty & _MENU:
            self._draw_selected()
        
        if self.dirty & _REFRESH:
            self._draw_status()
        
        self._show_queue()
        self.dirty = 0
        
    def exit_state(self):
        return