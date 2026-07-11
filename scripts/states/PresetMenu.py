
from states.PresetInteract import PresetInteract


class PresetMenu:
    def __init__(self, app, preset_data):
        self.app = app
        self.preset_data_full = preset_data
        self.current_index_preset = 0
        self.preset_data_select = str(self.preset_data_full[0])
        self.needs_draw = True

    def exit_state(self):
        self.app.state_manager.pop_state()

    def draw(self):
        if not self.needs_draw:
            return

        self.app.display.custom_message(self.preset_header(), x_axis=0, y_axis=0, fill_all=True, wrap=False)
        self.app.display.custom_message(self.preset_data_select, x_axis=0, y_axis=8, wrap=True, fill_all=False)
        self.app.display.custom_message('back        send', fill_all=False, x_axis=0, y_axis=56, wrap=False)

        self.needs_draw = False

    def handle_input(self, event, event_type):
        if event is None:
            return

        if event_type == 'button':
            self.app.state_manager.replace_state(PresetInteract(self.app,
            preset_data=self.preset_data_full, current_index= self.current_index_preset))

        if event_type in ('dial', 'switch'):
            self.current_index_preset = (self.current_index_preset + event) % len(self.preset_data_full)
            self.preset_data_select = str(self.preset_data_full[self.current_index_preset])
            self.needs_draw = True

    def enter_state(self):
        self.needs_draw = True

    def update(self):
        return

    def preset_header(self):
        prefix = 'PRESET' + str(self.current_index_preset + 1) + '/'
        suffix = '...'
        preview_length = 16 - len(prefix) - len(suffix)
        preview = self.preset_data_select[:preview_length] if preview_length > 0 else ''
        return prefix + preview + suffix






