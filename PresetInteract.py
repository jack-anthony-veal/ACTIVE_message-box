import math

from config import BUTTON_PRESS, DIAL_EVENT
from states.NotifyState import Notify, ErrorState


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

        final = ''
        x_axis = 0

        try:
            for index, option in enumerate(self.options):
                if index == self.current_index:
                    final = final + ' > ' + option.upper()
                else:
                    final = final + '' +  option.lower()

            x_axis = math.floor((128 // 2) - (len(final) * 8) // 2)


        except Exception as MathErr:
            self.app.state_manager.replace_state(ErrorState(self.app, MathErr, 32))
            return

        try:
            self.app.display.custom_message(final, wrap=False, fill_all=False,
                                        fill_start_line=56, fill_x_axis=128, fill_y_axis=8,
                                        y_axis=56, x_axis=x_axis
                                        )
        except Exception as ERR:
            self.app.state_manager.replace_state(ErrorState(self.app, ERR, 21))
            return


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

        self.app.display.custom_message(self.state_screen, fill_all=True, x_axis=0, y_axis=0, wrap=True)

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
