import math
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
        if _type == 'button' and event is not None:
            if self.current_index == 0:
                self.app.state_manager.pop_state()

            elif self.current_index == 1:
                self.app.state_manager.replace_state(SendingState(self.app, self.send_data))


        if _type == 'dial' and event is not None:
            self.current_index = (self.current_index + event) % len(self.options)
            self.index_changed = True

    def draw(self):
        if not self.index_changed: return

        final = ''
        x_axis = 0
        print(final)
        error_raised = False
        for index, option in enumerate(self.options):
            if index == self.current_index:
                final = final + ' > ' + option.upper()
                x_axis += len(' > ' + option.upper())
            else:
                final = final + '   ' +  option.lower()
                x_axis += len(option.lower())

            try:
                centre = 128 / 2
                x_axis = centre - math.floor((x_axis / 2))
                x_axis = math.floor(x_axis)

            except Exception as MathErr:
                error_raised=True
                x_axis = 0

            self.index_changed = False

            try:
                self.app.display.custom_message(final, wrap=False, fill_all=False,
                                            fill_start_line=56, fill_x_axis=128, fill_y_axis=8,
                                            y_axis=56, x_axis=0
                                            )
            except Exception as ERR:
                self.app.state_manager.replace_state(ErrorState(self.app, ERR, 0))


    def exit_state(self):
        return


class SendingState:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.state_screen = 'Sending... :00000'

    def enter_state(self):
        self.draw()

    def draw(self):
        self.app.display.custom_message()
        self.app.display.custom_message(self.state_screen, fill_all=True, x_axis=0, y_axis=0, wrap=True)
        success = False
        data = None

        try:
            success, data = self.app.message_api.send_preset(self.data)
        except Exception as sendError:
            self.app.state_manager.replace_state(ErrorState(self.app, sendError, 11))

        if success:
            self.app.state_manager.replace_state(Notify(self.app, title="Success!", data="presets successfully sent."))
        else:
            self.app.state_manager.replace_state(HTTPError(ErrorState(self.app, data, 0)))


    def update(self):
        return

    def exit_state(self):
        return
