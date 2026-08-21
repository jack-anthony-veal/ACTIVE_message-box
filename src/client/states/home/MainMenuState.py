from config import BUTTON_PRESS, RIGHT_DIAL, LEFT_DIAL
from states.presets.LoadingPresetsState import LoadingPresetsState
from states.settings.settings_navigate import SettingsNav


class MainMenuCycleState:
    def __init__(self, app, message_preview=None):
        self.app = app
        self.options = ["Message", "Presets", "Settings"]
        self.previews = [
            message_preview,
            "Open saved message presets",
            "Device and network settings",
        ]
        self.icons = ("menu_messages", "menu_presets", "menu_settings")
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
            if self.current_index == 1:
                self.app.state_manager.push_state(LoadingPresetsState(self.app))
            elif self.current_index == 2:
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
                selected_icon=self.icons[index] + "_selected",
            )
        right = "Open" if self.current_index in (1, 2) else ""
        display.draw_nav_bar(
            left="Rotate", right=right,
            left_icon="action_scroll",
            right_icon="nav_enter_select" if right else None,
        )
        self.index_updated = False

    def move_selection(self, direction):
        self.current_index = (self.current_index + direction) % len(self.options)
        self.index_updated = True
