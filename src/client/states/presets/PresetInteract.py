from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, CONTENT_BOTTOM, CONTENT_TOP, DIAL_EVENT, ERROR_HTTP_POST,
    ERROR_UNKNOWN, LINE_HEIGHT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX,
    SCREEN_MARGIN, SCREEN_WIDTH,
)
from states.NotifyState import Notify, ErrorState
_BACK_INDEX = 0
_SEND_INDEX = 1

class PresetInteract:
    def __init__(self, app, preset_data, current_index):
        self.app = app
        self.current_index = 0
        self.options = ["BACK", "SEND"]
        self.index_changed = True
        self.preset_data = preset_data
        self.send_data = preset_data[current_index]

    def enter_state(self):
        self.draw()

    def update(self):
        return

    def handle_input(self, event, _type):
        if event is None: return

        if _type == BUTTON_PRESS:
            if self.current_index == _BACK_INDEX:
                self.app.state_manager.reset()
                return
            elif self.current_index == _SEND_INDEX:
                self.app.state_manager.replace_state(SendingState(self.app, self.send_data))
                return

        if _type == DIAL_EVENT and event is not None:
            self.current_index = (self.current_index + event) % len(self.options)
            self.index_changed = True
            return

    def draw(self):
        if not self.index_changed: return
        self.index_changed = False

        display = self.app.display
        display.begin_screen("Send preset")
        display.draw_text_block(
            self.send_data,
            SCREEN_MARGIN,
            CONTENT_TOP + LINE_HEIGHT,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            bottom=CONTENT_BOTTOM,
        )
        display.draw_nav_bar(
            left="Back",
            right="Send",
            selected=(
                NAV_LEFT_INDEX
                if self.current_index == _BACK_INDEX
                else NAV_RIGHT_INDEX
            ),
            left_icon=ICONS["navigation"]["back"],
            right_icon=ICONS["navigation"]["send"],
        )


    def exit_state(self):
        return


class SendingState:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.state_screen = 'Sending... :00000'
        self.shown = False

    def enter_state(self):
        self.draw()

    def draw(self):
        if self.shown: return
        self.shown = True

        self.app.display.draw_loading(
            "Sending preset", ICONS["state"]["sending"]
        )

        try:
            success, data = self.app.message_api.send_preset(self.data)
        except Exception as sendError:
            self.app.state_manager.replace_state(
                ErrorState(self.app, sendError, ERROR_HTTP_POST)
            )
            return

        if success:
            self.app.state_manager.replace_state(Notify(self.app, title="Success!", data="presets successfully sent."))
            return
        else:
            self.app.state_manager.replace_state(
                ErrorState(self.app, data, ERROR_UNKNOWN)
            )
            return


    def update(self):
        return

    def exit_state(self):
        return
