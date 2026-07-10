import time

class PresetMenu:
    def __init__(self, app):
        self.app = app
        self.current_index_preset = 0
        self.index_switched_preset = False
        self.preset_data_full = None
        self.preset_data_select = None
        self.running=False

    def exit_state(self):
        ...

    def draw(self):
        if self.index_switched_preset:
            self.preset_data_select = self.preset_data_full[self.current_index_preset]
            time.sleep_ms(10)
            self.preset_body()
            time.sleep_ms(10)
            self.app.display.custom_message(self.preset_header(),x_axis=0, y_axis=0, fill_all=True, wrap=False)
            self.app.display.custom_message(self.preset_data_select, x_axis=0, y_axis=8, wrap=True, fill_all=False)
            self.index_switched_preset = False
        else: return


    def handle_input(self, event, event_type):
        if event_type == 'button' and event is not None:
            print('button')
            return

        if event_type == 'switch' and event is not None:
            index_direction = 1 if event else -1  # Added to remove redundancy
            self.current_index_preset = (self.current_index_preset + index_direction) % len(self.preset_data_full)
            self.index_switched_preset = True
            return
        else:
            return


    def enter_state(self):
        self.app.state_manager.current_state = self # ensure current is self
        self.app.display.custom_message("Loading...", x_axis=0, y_axis=8, fill_all=True, wrap = False)
        new_data, preset_data = self.app.message_api.load_presets()

        self.preset_data_full = preset_data
        self.preset_data_select = str(self.preset_data_full[0])

        self.index_switched_preset = True

        return None


    def update(self):
        return



    def preset_header(self):
        index_current = self.current_index_preset  # calls current index
        header_data = self.preset_data_full[index_current]

        [header_data.join(str(line) + '\n') for line in header_data if type(header_data == list)]

        str_ext: str = f'PRESET{str(index_current+1)}/'  # make changeable
        str_sff: str = '...'
        length_data: int = (16 - (len(str_ext) + len(str_sff)))
        max_to_show: int = length_data if int(length_data) < 16 else 0

        header_data = header_data[0:int(max_to_show)] if max_to_show > 0 else ''

        data_final = str(str_ext) + str(header_data) + str(str_sff)

        return data_final  # returns heade


    def preset_body(self):
        data_body = self.preset_data_select
        lines = []
        while len(data_body) > 16:
            lines.append(data_body[:16])
            data_body = data_body[16:]

        if data_body:
            lines.append(data_body)

        self.preset_data_select = lines


class PresetOptionsMenu:
    ...


