from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, COLOR_TEXT_MUTED, CONTENT_BOTTOM, CONTENT_TOP, DIAL_EVENT,
    FONT_HEIGHT, LINE_HEIGHT, NAV_LEFT_INDEX, NAV_RIGHT_INDEX, SCREEN_MARGIN,
    SCREEN_WIDTH, SPACE_SM,
)
from libraries.utils.timezone import format_uk_time
from states.keyboard import Keyboard
from states.presets.PresetInteract import SendingState
from states.proc.two_mode import TwoModeController


_SEND = 0
_BACK = 1


class MessageDisplay:
    def __init__(self, app, message=None):
        self.app = app
        self.message = message
        self.controller = TwoModeController(2)
        self.scroll_offset = 0
        self.needs_draw = True

    def _record(self):
        if type(self.message) is dict:
            return self.message
        if self.message is not None:
            return {"sender": "saved", "text": str(self.message), "utc": ""}
        record = self.app.storage.newest_message()
        if record is None:
            return {"sender": "", "text": "No saved messages", "utc": ""}
        return record

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
            self._record().get("text", ""),
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
        )
        return lines if lines is not None else [self._record().get("text", "")]

    def _max_scroll(self):
        body_height = CONTENT_BOTTOM - (CONTENT_TOP + LINE_HEIGHT + SPACE_SM)
        return max(0, len(self._lines()) * LINE_HEIGHT - body_height)

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
            print("SCROLL|message|{}".format(self.scroll_offset))
            return
        if event_type != BUTTON_PRESS:
            return
        selected = self.controller.activate()
        self.needs_draw = True
        if selected is None:
            print("MENU|message|open")
            return
        print("MENU|message|activate|{}".format(selected))
        if selected == _BACK:
            self.app.state_manager.pop_state()
            return
        return_buffer = bytearray()
        sending = SendingState(self.app, return_buffer, label="message")
        self.app.state_manager.push_state(
            Keyboard(self.app, sending, return_buffer, "Type message")
        )

    def draw(self):
        if not self.needs_draw:
            return
        self.needs_draw = False
        record = self._record()
        sender = record.get("sender") or "Unknown"
        display = self.app.display
        display.begin_screen("From " + str(sender).title())
        timestamp = format_uk_time(record.get("utc", ""))
        if timestamp:
            display.text(
                timestamp,
                SCREEN_MARGIN,
                CONTENT_TOP,
                COLOR_TEXT_MUTED,
            )
        body_top = CONTENT_TOP + LINE_HEIGHT + SPACE_SM
        for index, line in enumerate(self._lines()):
            y = body_top + index * LINE_HEIGHT - self.scroll_offset
            if y < body_top or y + FONT_HEIGHT > CONTENT_BOTTOM:
                continue
            display.text(line, SCREEN_MARGIN, y)
        if self.controller.menu_open:
            selected = (
                NAV_LEFT_INDEX
                if self.controller.action_index == _BACK
                else NAV_RIGHT_INDEX
            )
            display.draw_nav_bar(
                left="Back",
                right="Send",
                selected=selected,
                left_icon=ICONS["navigation"]["back"],
                right_icon=ICONS["navigation"]["send"],
            )
        else:
            display.draw_nav_bar()
