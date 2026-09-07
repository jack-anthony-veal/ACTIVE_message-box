from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, CONTENT_BOTTOM, CONTENT_TOP, DIAL_EVENT, ERROR_HTTP_POST,
    ERROR_UNKNOWN, FONT_HEIGHT, LINE_HEIGHT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX,
    SCREEN_MARGIN, SCREEN_WIDTH,
)
from states.NotifyState import ErrorState, Notify
from states.proc.two_mode import TwoModeController


_BACK = 0
_SEND = 1


class PresetInteract:
    def __init__(self, app, preset_data, current_index):
        self.app = app
        self.send_data = str(preset_data[current_index])
        self.controller = TwoModeController(2)
        self.scroll_offset = 0
        self.needs_draw = True

    def enter_state(self):
        self.controller.hide_menu()
        self.needs_draw = True
        self.draw()

    def exit_state(self):
        return

    def update(self):
        return

    def _lines(self):
        lines = self.app.display.text_lines(
            self.send_data, SCREEN_WIDTH - SCREEN_MARGIN * 2
        )
        return lines if lines is not None else [self.send_data]

    def _max_scroll(self):
        return max(
            0,
            len(self._lines()) * LINE_HEIGHT - (CONTENT_BOTTOM - CONTENT_TOP),
        )

    def handle_input(self, event, event_type=None):
        if event is None or event_type is None:
            return
        if event_type == DIAL_EVENT:
            if self.controller.rotate(event):
                self.needs_draw = True
                return
            self.scroll_offset += event * LINE_HEIGHT
            self.scroll_offset = max(0, min(self.scroll_offset, self._max_scroll()))
            self.needs_draw = True
            print("SCROLL|preset|{}".format(self.scroll_offset))
            return
        if event_type != BUTTON_PRESS:
            return
        selected = self.controller.activate()
        self.needs_draw = True
        if selected is None:
            print("MENU|preset|open")
        elif selected == _BACK:
            self.app.state_manager.pop_state()
        elif selected == _SEND:
            self.app.state_manager.replace_state(
                SendingState(self.app, self.send_data, label="preset")
            )

    def draw(self):
        if not self.needs_draw:
            return
        self.needs_draw = False
        display = self.app.display
        display.begin_screen("Preset detail")
        for index, line in enumerate(self._lines()):
            y = CONTENT_TOP + index * LINE_HEIGHT - self.scroll_offset
            if y < CONTENT_TOP or y + FONT_HEIGHT > CONTENT_BOTTOM:
                continue
            display.text(line, SCREEN_MARGIN, y)
        if self.controller.menu_open:
            display.draw_nav_bar(
                left="Back",
                right="Send",
                selected=(
                    NAV_LEFT_INDEX
                    if self.controller.action_index == _BACK
                    else NAV_RIGHT_INDEX
                ),
                left_icon=ICONS["navigation"]["back"],
                right_icon=ICONS["navigation"]["send"],
            )
        else:
            display.draw_nav_bar()


class SendingState:
    def __init__(self, app, data, label="preset"):
        self.app = app
        self.data = data
        self.label = label
        self.started = False

    def enter_state(self):
        self.draw()

    def draw(self):
        if self.started:
            return
        self.started = True
        self.app.display.draw_loading(
            "Sending " + self.label, ICONS["state"]["sending"]
        )
        try:
            if type(self.data) in (bytes, bytearray):
                text = bytes(self.data).decode("utf-8")
            else:
                text = str(self.data)
            sender = getattr(self.app.message_api, "send_message", None)
            if sender is None:
                sender = self.app.message_api.send_preset
            success, detail = sender(text)
        except Exception as error:
            self.app.state_manager.replace_state(
                ErrorState(self.app, str(error), ERROR_HTTP_POST)
            )
            return
        if success:
            print("MESSAGE|sent")
            self.app.state_manager.replace_state(
                Notify(self.app, "Message sent.", "Success")
            )
        else:
            self.app.state_manager.replace_state(
                ErrorState(self.app, detail, ERROR_UNKNOWN)
            )

    def update(self):
        return

    def handle_input(self, event=None, event_type=None):
        return

    def exit_state(self):
        return
