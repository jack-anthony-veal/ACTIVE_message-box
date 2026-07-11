class PresetMenu:
    def __init__(self, app, preset_data):
        self.app = app
        self.preset_data_full = preset_data
        self.current_index_preset = 0
        self.preset_data_select = str(self.preset_data_full[0])
        self.needs_draw = True

    def exit_state(self):
        return

    def draw(self):
        if not self.needs_draw:
            return

        self.app.display.custom_message(self.preset_header(), x_axis=0, y_axis=0, fill_all=True, wrap=False)
        self.app.display.custom_message(self.preset_data_select, x_axis=0, y_axis=8, wrap=True, fill_all=False)
        self.needs_draw = False

    def handle_input(self, event, event_type=None):
        if event is None:
            return

        if event_type == 'button':
            print(self.preset_data_select)
            return

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


class PresetOptionsMenu:
    def __init__(self, app):
        self.app = app
        self.options = ["BACK", "SEND"]
        self.index_current = 0
        self.options_display = None
        self.index_changed = False


    def enter_state(self):
        self.index_changed = True
        self.index_current = 0



    def update(self):
        ...

    def handle_input(self, event, event_type):
        if event_type == 'button' and event is not None:
            ...


        if event_type == 'dial' and event is not None:
            self.index_changed = True
            index = self.index_current
            options = self.options

            new_index = (index + event) % len(options)
            options_display = []
            for line, option in enumerate(options):
                if new_index == line:
                    options_display.append(' > ' + str(option.upper()))
                else:
                    options_display.append(option.lower())

            self.index_current = new_index
            self.index_changed = True
            return

        self.index_changed = False

    def draw(self):
        if self.index_changed and self.options_display is not None:
            self.app.display.custom_message(self.options_display,
                                            fill_start_line=56,
                                            fill_x_axis=128, fill_y_axis=8,
                                            x_axis=0, y_axis=56, wrap=False
                                            )
            self.index_changed = False
        else: return








