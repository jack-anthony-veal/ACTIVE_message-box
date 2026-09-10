from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, CONTENT_TOP, DIAL_EVENT, MAX_PRESETS, NAV_LEFT_INDEX,
    NAV_RIGHT_INDEX, SCREEN_MARGIN, SCREEN_WIDTH,
)
from states.presets.PresetInteract import PresetInteract
from states.proc.base_display import menu_positions
from states.proc.two_mode import TwoModeController


_OPEN = 0
_BACK = 1


class PresetMenu:
    def __init__(self, app, preset_data):
        self.app = app
        self.preset_data_full = list(preset_data)[:MAX_PRESETS]
        self.current_index_preset = 0
        self.preset_data_select = (
            str(self.preset_data_full[0]) if self.preset_data_full else ""
        )
        self.controller = TwoModeController(2)
        self.needs_draw = True

    def enter_state(self):
        self.controller.hide_menu()
        self.needs_draw = True
        self.draw()

    def exit_state(self):
        return

    def update(self):
        return

    def handle_input(self, event, event_type=None):
        if event is None or event_type is None:
            return
        if event_type == DIAL_EVENT:
            if self.controller.rotate(event):
                self.needs_draw = True
                return
            if self.preset_data_full:
                self.current_index_preset = (
                    self.current_index_preset + event
                ) % len(self.preset_data_full)
                self.preset_data_select = str(
                    self.preset_data_full[self.current_index_preset]
                )
                self.needs_draw = True
            return
        if event_type != BUTTON_PRESS:
            return
        selected = self.controller.activate()
        self.needs_draw = True
        if selected is None:
            print("MENU|presets|open")
            return
        if selected == _BACK or not self.preset_data_full:
            self.app.state_manager.pop_state()
        elif selected == _OPEN:
            self.app.state_manager.push_state(PresetInteract(
                self.app,
                preset_data=self.preset_data_full,
                current_index=self.current_index_preset,
            ))

    def draw(self):
        if not self.needs_draw:
            return
        self.needs_draw = False
        display = self.app.display
        display.begin_screen("Presets", "{} / 5".format(len(self.preset_data_full)))
        if not self.preset_data_full:
            display.draw_text_block(
                "No presets saved",
                SCREEN_MARGIN,
                CONTENT_TOP + 32,
                SCREEN_WIDTH - SCREEN_MARGIN * 2,
            )
        else:
            for item_index, row_index in menu_positions(
                len(self.preset_data_full), self.current_index_preset
            ):
                display.draw_menu_row(
                    row_index,
                    "Preset {}".format(item_index + 1),
                    subtitle=str(self.preset_data_full[item_index]),
                    selected=item_index == self.current_index_preset,
                    icon=ICONS["menu"]["presets"],
                    selected_icon=ICONS["menu"]["presets_selected"],
                )
        if self.controller.menu_open:
            display.draw_nav_bar(
                left="Back",
                right="Open",
                selected=(
                    NAV_LEFT_INDEX
                    if self.controller.action_index == _BACK
                    else NAV_RIGHT_INDEX
                ),
                left_icon=ICONS["navigation"]["back"],
                right_icon=ICONS["navigation"]["select"],
            )
        else:
            display.draw_nav_bar()

    def preset_header(self):
        if not self.preset_data_full:
            return "No presets"
        return "Preset {} of {}".format(
            self.current_index_preset + 1, len(self.preset_data_full)
        )
