from config import BUTTON_PRESS, DIAL_EVENT
from config.ui_config import CONTENT_BOTTOM, CONTENT_TOP, SCREEN_MARGIN, SCREEN_WIDTH
from states.NotifyState import Notify, ErrorState
_OTHER = 1 << 0
_NON_FATAL_API = 1 << 1
_NON_FATAL_WIFI= 1 << 2
_NON_FATAL_HTTP= 1 << 3
_NON_FATAL = 1 << 4

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
            if self.current_index == 0:
                self.app.state_manager.reset() # TODO: go back twice
                return
            elif self.current_index == 1:
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
            CONTENT_TOP + 20,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            bottom=CONTENT_BOTTOM,
        )
        display.draw_nav_bar(
            left="Back",
            right="Send",
            selected=0 if self.current_index == 0 else 2,
            left_icon="nav_back",
            right_icon="nav_send",
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

        self.app.display.draw_loading("Sending preset", "state_sending")

        try:
            success, data = self.app.message_api.send_preset(self.data)
        except Exception as sendError:
            self.app.state_manager.replace_state(ErrorState(self.app, sendError, 11))
            return

        if success:
            self.app.state_manager.replace_state(Notify(self.app, title="Success!", data="presets successfully sent."))
            return
        else:
            self.app.state_manager.replace_state(ErrorState(self.app, data, 0))
            return


    def update(self):
        return

    def exit_state(self):
        return
