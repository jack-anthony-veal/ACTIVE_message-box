from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, HOME_PRESETS_INDEX, HOME_SETTINGS_INDEX, LEFT_DIAL,
    RIGHT_DIAL, HOME_MESSAGE_INDEX
)
from states.presets.LoadingPresetsState import LoadingPresetsState
from states.settings.settings_navigate import SettingsNav
from states.message.message import MessageDisplay


class MainMenuCycleState:
    def __init__(self, app, message_preview=None):
        self.app = app
        self.message_record = message_preview if type(message_preview) is dict else None
        preview_text = (
            message_preview.get("text")
            if type(message_preview) is dict
            else message_preview
        )
        self.options = ["Message", "Presets", "Settings"]
        self.previews = [
            preview_text,
            "Open saved message presets",
            "Device and network settings",
        ]
        self.icons = (
            ICONS["menu"]["messages"],
            ICONS["menu"]["presets"],
            ICONS["menu"]["settings"],
        )
        self.selected_icons = (
            ICONS["menu"]["messages_selected"],
            ICONS["menu"]["presets_selected"],
            ICONS["menu"]["settings_selected"],
        )
        self.running = False
        self.current_index = 0
        self.index_updated = True

    def enter_state(self):
        self.app.display.power_on()
        self.index_updated = True
        self.draw()

    def exit_state(self):
        self.running = False

    def handle_input(self, event, event_type=None):
        if event is None or event_type is None:
            return
        if event_type == BUTTON_PRESS:
            if self.current_index == HOME_MESSAGE_INDEX:
                self.app.state_manager.push_state(
                    MessageDisplay(self.app, self.message_record)
                )
            elif self.current_index == HOME_PRESETS_INDEX:
                self.app.state_manager.push_state(LoadingPresetsState(self.app))
            elif self.current_index == HOME_SETTINGS_INDEX:
                self.app.state_manager.push_state(SettingsNav(self.app))
            return
        if event in (RIGHT_DIAL, LEFT_DIAL):
            self.move_selection(event)

    def update(self):
        return

    def draw(self):
        if not self.index_updated:
            return
        display = self.app.display
        display.begin_screen("Home", "Rotate")
        for index, option in enumerate(self.options):
            display.draw_menu_row(
                index,
                option,
                selected=index == self.current_index,
                subtitle=self.previews[index],
                icon=self.icons[index],
                selected_icon=self.selected_icons[index],
            )
        right = "Open"
        display.draw_nav_bar(
            left="Rotate", right=right,
            left_icon=ICONS["action"]["scroll"],
            right_icon=ICONS["navigation"]["select"],
        )
        self.index_updated = False

    def move_selection(self, direction):
        self.current_index = (self.current_index + direction) % len(self.options)
        self.index_updated = True
