import math

from config import BUTTON_PRESS, RIGHT_DIAL, LEFT_DIAL
from config.config import MENU_Y_AXIS
from states.NotifyState import ErrorState
from states.presets.LoadingPresetsState import LoadingPresetsState
from states.settings.settings_navigate import SettingsNav


class MainMenuCycleState:
    def __init__(self, app, message_preview=None):
        self.app = app
        self.options = ["message", "presets", "settings"]
        self.previews = [
            message_preview,
            "Open to view presets...",
            "No settings yet",
        ]
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
        if event is None or event_type is None: return

        if event_type == BUTTON_PRESS:
            if self.current_index == 1:
                self.app.state_manager.push_state(LoadingPresetsState(self.app))
                return
            if self.current_index == 2:
                self.app.state_manager.push_state(SettingsNav(self.app))
                return

        elif event in (RIGHT_DIAL, LEFT_DIAL):
            self.move_selection(event)

    def update(self):
        return

    def draw(self):
        if not self.index_updated: return
        self.app.display.custom_message(
            self.previews[self.current_index],
            x_axis=0,
            y_axis=8,
            wrap=True,
            fill_all=True,
        )
        self.show_menu_bar()
        self.index_updated = False

    def show_menu_bar(self):
        try:
            x_axis = (len(self.options[self.current_index] + ' > ') + 1) * 8
            centre = 128 / 2
            x_axis = centre - math.floor((x_axis / 2))
            x_axis = math.floor(x_axis)

        except Exception as IndexMathERR:
            print(IndexMathERR)
            self.app.state_manager.replace_state(state=ErrorState(self.app, str(str(IndexMathERR)), 31))
            return


        try:
            self.app.display.custom_message(
            ' > ' + self.options[self.current_index],
            x_axis=x_axis,
            y_axis=MENU_Y_AXIS,
            fill_start_line=MENU_Y_AXIS,
            fill_x_axis=128,
            fill_y_axis=8,
            wrap=False,
            )
        except Exception as DisplayErr:
            self.app.state_manager.replace_state(state=ErrorState(self.app, str(str(DisplayErr)), 21))
            return


    def move_selection(self, direction):
        self.current_index = (self.current_index + direction) % len(self.options)
        self.index_updated = True
