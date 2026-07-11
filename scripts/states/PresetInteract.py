import math

from states import PresetMenu


class PresetInteract:
    def __init__(self, app, preset_data):
        self.app = app
        self.current_index = 0
        self.options = ["BACK", "SEND"]
        self.index_changed = False
        self.send_data = preset_data

    def enter_state(self):
        self.draw()

    def update(self):
        ...

    def handle_input(self, event, _type):
        if _type == 'button' and event is not None:
            if self.current_index == 0:
                self.app.state_manager.replace_state(PresetMenu(self.app, preset_data=None))

            elif self.current_index == 1:
                try:
                    self.app.message_api.send_message(self.send_data)

                except Exception as HTTPErr:
                    self.app.state_manager.replace_state('error_state')

                self.app.state_manager.replace_state('hi')
                self.app.state_manager.reset()

        if _type == 'dial' and event is not None:
            self.current_index = (self.current_index + event) % len(self.options)
            self.index_changed = True

    def draw(self):
        if not self.index_changed: return
        display_message = []
        x_axis = 0
        for index, option in enumerate(self.options):
            if index == self.current_index:
                display_message.append(' > ' + option.upper())
                x_axis += len(' > ' + option.upper())
            else:
                display_message.append(option.lower())
                x_axis += len(option.lower())

        centre = 128 / 2
        x_axis = centre - math.floor((x_axis / 2))
        x_axis = math.floor(x_axis)

        self.app.display.custom_message(display_message, wrap=False,
                                        fill_start_line=56, fill_x_axis=128, fill_y_axis=8,
                                        y_axis=8, x_axis=x_axis
                                        )
        self.index_changed = False

    def exit_state(self):
        self.app.display.custom_message()

class SendingState:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.state_screen = ''

    def enter_state(self):
        try:
            self.app.message_api.send_message(self.data)

        except Exception as HTTPErr:
            self.app.state_manager.replace_state()