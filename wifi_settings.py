from micropython import const
import time
import network

from libraries.utils.menutools import MenuTools

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


class WifiSettings:
    def __init__(self, app, kb_data=None):
        self.app = app
        self.station = network.WLAN(network.STA_IF)

        self.saved_ssid = WIFI_SSID
        self.saved_pass = WIFI_PASSWORD
        self._load_saved_credentials()
        self.return_kb = kb_data
        
        
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

    def _load_saved_credentials(self):
        import configparser
        _config_ = configparser.ConfigParser()
        try:
            if self.return_kb is not None:
                with open("../return-kb-data.tmp", "w") as return_file:
                    data = return_file.readlines()
                    return_file.close()
                    
                try:
                    _config_['ssid'] = data[0]
                    _config_['pass'] = data[1]
                    
                    self.saved_ssid = data[0]
                    self.saved_pass = data[1]
                    
                    with open('../config/network.ini') as conf:
                        conf.write(_config_)
                        conf.close()
                        
                except Exception as err:
                    print("err")
                    self.return_kb = None
                    
            elif self.return_kb is None:
                try:
                    _config_.read('../config/network.ini')
                    self.saved_ssid, self.saved_pass = _config_.get('ssid', 'pass')
                except Exception as err:
                    print(err) # Add err messgae in this sect
                    
                    
                
                
                    
            
        except OSError:
            pass

    def enter_state(self):
        self.app.display.oled.fill(0)
        errors = []
        station = self.station
        scanned_networks = ()

        try:
            station.active(False)
            time.sleep_ms(20)
            station.active(True)
            station.disconnect()
            time.sleep_ms(20)
        except Exception as err:
            errors.append("station reset: " + str(err))

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
            self.app.state_manager.push_state(Keyboard(app, WifiSettings))
            self.exit_state()
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
                self.app.state_manager.replace_state(Keyboard(self.app, self))
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



