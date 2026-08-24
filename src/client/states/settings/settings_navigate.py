_DIRTY = 1 << 0

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS as BUTTON_EVENT, DIAL_EVENT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX,
)
from states.proc.base_display import BaseScroll
from states.settings.WIFI import WifiState


SETTINGS_ITEMS = (
    ("Account", ICONS["menu"]["account"]),
    ("Device", ICONS["menu"]["device"]),
    ("Wi-Fi", ICONS["menu"]["wifi"]),
    ("Graphics", ICONS["menu"]["graphics"]),
    ("TBD", ICONS["action"]["question"]),
)

_ACTION_EDIT = 0
_ACTION_BACK = 1
_SETTINGS_WIFI_INDEX = 2


class SettingsNav:
    def __init__(self, app):
        self.app = app
        self.index_flag = 0  # shifts if main screen moves
        self.settings_flag = 1
        self.menu_flag = 0  # becomes menu dirty if pressed
        self.current_index = 0

        self.settings_menu = tuple(item[0] for item in SETTINGS_ITEMS)
        self.icons = tuple(item[1] for item in SETTINGS_ITEMS)
        self.options_menu = ("Edit", "Back")
        self.option_icons = (
            ICONS["navigation"]["edit"],
            ICONS["navigation"]["back"],
        )
        self.last_opt_settings = 0

        self.menu_size = len(self.options_menu)
        self.settings_size = len(self.settings_menu)
        self.SETTINGS_CONTROLLER = BaseScroll(self.settings_menu)

    def enter_state(self):
        self.settings_flag = 1
        self.menu_flag = 0
        self.current_index = self.last_opt_settings
        self.index_flag |= _DIRTY
        self.draw()

    def exit_state(self):
        pass

    def handle_input(self, _event, _type):
        if _type == DIAL_EVENT:
            active_size = self.settings_size if self.settings_flag & _DIRTY else self.menu_size
            self.current_index = (self.current_index + _event) % active_size
            self.index_flag |= _DIRTY
            self.draw()
            return

        if _type == BUTTON_EVENT and (self.settings_flag & _DIRTY):
            self.last_opt_settings = self.current_index
            self.settings_flag = 0
            self.menu_flag |= _DIRTY
            self.current_index = 0
            self.index_flag |= _DIRTY
            self.draw()
            return

        if _type == BUTTON_EVENT and (self.menu_flag & _DIRTY):
            if self.current_index == _ACTION_BACK:
                self.current_index = self.last_opt_settings
                self.menu_flag = 0
                self.settings_flag |= _DIRTY
                self.index_flag |= _DIRTY
                from states.home.LoadingMainMenuState import LoadingMainMenuState
                self.app.state_manager.push_state(LoadingMainMenuState(self.app))
                return

                return
            if (
                self.current_index == _ACTION_EDIT
            ):
                match self.last_opt_settings:
                    case 0:
                        return                    
                    case _SETTINGS_WIFI_INDEX:
                        self.app.state_manager.push_state(WifiState(self.app))
    def draw(self):
        if not self.index_flag & _DIRTY:
            return

        display = self.app.display
        if self.settings_flag & _DIRTY:
            display.begin_screen("Settings", "Rotate")
            for item_index, row_index in self.SETTINGS_CONTROLLER(
                self.current_index
            ):
                icon = self.icons[item_index]
                display.draw_menu_row(
                    row_index,
                    self.settings_menu[item_index],
                    selected=item_index == self.current_index,
                    icon=icon,
                )
        elif self.menu_flag & _DIRTY:
            self._draw_nav_bar(self.current_index)
        self.index_flag = 0

    def _draw_nav_bar(self, index=None):
        self.app.display.draw_nav_bar(
            left=self.options_menu[_ACTION_BACK],
            right=self.options_menu[_ACTION_EDIT],
            selected=(
                NAV_RIGHT_INDEX if index == _ACTION_EDIT else NAV_LEFT_INDEX
            ) if index is not None else None,
            left_icon=self.option_icons[_ACTION_BACK],
            right_icon=self.option_icons[_ACTION_EDIT],
        )

    def update(self):
        return
