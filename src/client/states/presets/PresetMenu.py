from config import DIAL_EVENT, BUTTON_PRESS
from config.ui_config import CONTENT_BOTTOM, CONTENT_TOP, SCREEN_MARGIN, SCREEN_WIDTH
from states.presets.PresetInteract import PresetInteract


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
        display = self.app.display
        display.begin_screen(self.preset_header(), "Rotate")
        display.draw_text_block(
            self.preset_data_select,
            SCREEN_MARGIN,
            CONTENT_TOP + 20,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            bottom=CONTENT_BOTTOM,
        )
        display.draw_nav_bar(
            left="Rotate", right="Choose",
            left_icon="action_scroll", right_icon="nav_enter_select",
        )
        self.needs_draw = False

    def handle_input(self, event, event_type):
        if event is None:
            return
        if event_type == BUTTON_PRESS:
            self.app.state_manager.push_state(PresetInteract(
                self.app,
                preset_data=self.preset_data_full,
                current_index=self.current_index_preset,
            ))
            return
        if event_type == DIAL_EVENT:
            self.current_index_preset = (
                self.current_index_preset + event
            ) % len(self.preset_data_full)
            self.preset_data_select = str(
                self.preset_data_full[self.current_index_preset]
            )
            self.needs_draw = True

    def enter_state(self):
        self.needs_draw = True

    def update(self):
        return

    def preset_header(self):
        return "Preset {} of {}".format(
            self.current_index_preset + 1,
            len(self.preset_data_full),
        )
