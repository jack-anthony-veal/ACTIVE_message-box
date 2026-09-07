from assets.registry import ICONS
from config.config import BUTTON_PRESS, DIAL_EVENT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX
from states.proc.base_display import BaseScroll
from states.proc.two_mode import TwoModeController
from states.settings.WIFI import WifiState


SETTINGS_ITEMS = (
    ("Account", ICONS["menu"]["account"]),
    ("Device", ICONS["menu"]["device"]),
    ("Wi-Fi", ICONS["menu"]["wifi"]),
    ("Graphics", ICONS["menu"]["graphics"]),
    ("About", ICONS["action"]["question"]),
)

_ACTION_EDIT = 0
_ACTION_BACK = 1
_SETTINGS_WIFI_INDEX = 2


class SettingsNav:
    def __init__(self, app):
        self.app = app
        self.settings_menu = tuple(item[0] for item in SETTINGS_ITEMS)
        self.icons = tuple(item[1] for item in SETTINGS_ITEMS)
        self.options_menu = ("Edit", "Back")
        self.current_index = 0
        self.controller = TwoModeController(2)
        self.SETTINGS_CONTROLLER = BaseScroll(self.settings_menu)
        self.needs_draw = True

    def enter_state(self):
        self.controller.hide_menu()
        self.needs_draw = True
        self.draw()

    def exit_state(self):
        return

    def update(self):
        return

    def handle_input(self, event, event_type=None):
        if event is None or event_type is None:
            return
        if event_type == DIAL_EVENT:
            if not self.controller.rotate(event):
                self.current_index = (
                    self.current_index + event
                ) % len(self.settings_menu)
            self.needs_draw = True
            return
        if event_type != BUTTON_PRESS:
            return
        selected = self.controller.activate()
        self.needs_draw = True
        if selected is None:
            print("MENU|settings|open")
            return
        if selected == _ACTION_BACK:
            self.app.state_manager.pop_state()
        elif selected == _ACTION_EDIT and self.current_index == _SETTINGS_WIFI_INDEX:
            self.app.state_manager.push_state(WifiState(self.app))

    def draw(self):
        if not self.needs_draw:
            return
        self.needs_draw = False
        display = self.app.display
        display.begin_screen("Settings", "Rotate")
        for item_index, row_index in self.SETTINGS_CONTROLLER(self.current_index):
            display.draw_menu_row(
                row_index,
                self.settings_menu[item_index],
                selected=item_index == self.current_index,
                icon=self.icons[item_index],
            )
        if self.controller.menu_open:
            display.draw_nav_bar(
                left="Back",
                right="Edit",
                selected=(
                    NAV_RIGHT_INDEX
                    if self.controller.action_index == _ACTION_EDIT
                    else NAV_LEFT_INDEX
                ),
                left_icon=ICONS["navigation"]["back"],
                right_icon=ICONS["navigation"]["edit"],
            )
        else:
            display.draw_nav_bar()
