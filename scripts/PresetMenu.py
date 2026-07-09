class PresetMenu:
    def __init__(self, app):
        self.app = app
        self.current_index = 1
        self.index_switched = False
        self.preset_data_full = None
        self.preset_data_select = None

    def exit_state(self):
        ...

    def draw(self):
        if self.index_switched:
            self.preset_data_full = None
            self.preset_data_select = self.preset_data_full[self.current_index]
            self.preset_body()
            self.app.display.custom_message(self.preset_header(), fill_all=True, wrap=False)
            self.app.display.custom_message(self.preset_data_select, x_axis=0, y_axis=8, fill_all=False, wrap=True)
            self.index_switched = False


    def handle_input(self, event, event_type):
        if event_type == 'button' and event is not None:
            ...

        if event_type == 'switch' and event is not None:
            self.current_index += 1
            self.index_switched = True
            return


    def enter_state(self):
        self.app.display.custom_message("Loading...", x_axis=0, y_axis=8, fill_all=True)

        new_data, preset_data = self.app.message_api.load_presets()
        self.preset_data_full = preset_data
        self.preset_data_select = self.preset_data_full[self.current_index]

        self.index_switched = True

        return None



    def preset_header(self):
        if type(self.preset_data_select) != list: raise Exception("DATA NOT IN LIST!!!")

        index_current = self.current_index  # calls current index

        str_ext = f'PRESET{index_current + 1}/'  # make changeable
        str_sff = '...'
        header = self.preset_data_select[index_current][:16 - (len(str_ext) + len(str_sff))]

        data_final = str_ext + header + str_sff

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


