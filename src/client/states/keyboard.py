import time

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, COLOR_BACKGROUND, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_SELECTED_BG, COLOR_SELECTED_TEXT, COLOR_SURFACE, COLOR_TEXT,
    COLOR_TEXT_MUTED, CONTENT_TOP, DIAL_EVENT, KEYBOARD_BACKSPACE_HELP_Y,
    KEYBOARD_CASE_HELP_Y, KEYBOARD_DOUBLE_PRESS_MS, KEYBOARD_ENTER_HELP_Y,
    KEYBOARD_FRAME_INTERVAL_MS, KEYBOARD_KEY_HEIGHT, KEYBOARD_KEY_TEXT_Y_OFFSET,
    KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_X, KEYBOARD_KEY_Y,
    KEYBOARD_SELECTED_KEY_INDEX, KEYBOARD_TEXT_BOX_HEIGHT,
    KEYBOARD_TEXT_BOX_INSET, KEYBOARD_TEXT_COLUMNS, KEYBOARD_TEXT_LIMIT,
    KEYBOARD_TEXT_LINE_HEIGHT, KEYBOARD_TEXT_ROWS, KEYBOARD_TEXT_X,
    KEYBOARD_TEXT_Y, KEYBOARD_VISIBLE_KEYS, SCREEN_MARGIN, SCREEN_WIDTH,
    SPACE_SM,
)


_DIRTY_KEYS = 1
_DIRTY_TEXT = 2

ALPHABET_LOWER = "abcdefghijklmnopqrstuvwxyz0123456789 _.,!?@#£$&*()+-=:;/\\<~"
ALPHABET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _.,!?@#£$&*()+-=:;/\\<~"
ALPHABET_ = ALPHABET_LOWER
ALPHABET_SHIFT_ = ALPHABET_UPPER


class Keyboard:
    def __init__(self, app, last_state, return_buffer, kb_text="Begin Typing"):
        self.app = app
        self.display = app.display
        self.last_state = last_state
        self.return_buffer = return_buffer
        self.kb_text_ = kb_text
        self.upper_case = False
        self.alphabet = ALPHABET_LOWER
        self.alphabet_length = len(self.alphabet)
        self.current = 0
        self.text_buffer = []
        self.text_length = 0
        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        self.last_click_ms = time.ticks_ms()
        self.waiting_second_click = False
        self.last_frame = time.ticks_add(
            time.ticks_ms(), -KEYBOARD_FRAME_INTERVAL_MS
        )

    def enter_state(self):
        display = self.display
        display.begin_screen("Keyboard", "Rotate")
        display.draw_text_block(
            self.kb_text_,
            SCREEN_MARGIN,
            CONTENT_TOP + SPACE_SM,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=COLOR_TEXT_MUTED,
            max_lines=1,
            bottom=KEYBOARD_TEXT_Y,
        )
        display.fill_rect(
            KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET,
            KEYBOARD_TEXT_Y - KEYBOARD_TEXT_BOX_INSET,
            SCREEN_WIDTH - (KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET) * 2,
            KEYBOARD_TEXT_BOX_HEIGHT,
            COLOR_SURFACE,
        )
        display.rect(
            KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET,
            KEYBOARD_TEXT_Y - KEYBOARD_TEXT_BOX_INSET,
            SCREEN_WIDTH - (KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET) * 2,
            KEYBOARD_TEXT_BOX_HEIGHT,
            COLOR_BORDER,
        )
        display.text(
            "< Backspace    _ Space",
            SCREEN_MARGIN,
            KEYBOARD_BACKSPACE_HELP_Y,
            COLOR_TEXT_MUTED,
        )
        display.text(
            "Double press changes case",
            SCREEN_MARGIN,
            KEYBOARD_CASE_HELP_Y,
            COLOR_TEXT_MUTED,
        )
        display.text("~ Enter", SCREEN_MARGIN, KEYBOARD_ENTER_HELP_Y, COLOR_TEXT_MUTED)
        display.draw_nav_bar(
            left="Rotate",
            center="Case",
            right="Press",
            left_icon=ICONS["action"]["scroll"],
            center_icon=ICONS["navigation"]["edit"],
            right_icon=ICONS["navigation"]["select"],
        )
        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        self.draw(force=True)

    def exit_state(self):
        return

    def update(self):
        if (
            self.waiting_second_click
            and time.ticks_diff(time.ticks_ms(), self.last_click_ms)
            > KEYBOARD_DOUBLE_PRESS_MS
        ):
            self.waiting_second_click = False
            self._handle_button()
        self.draw()

    def handle_input(self, event, event_type=None):
        if event is None:
            return
        if event_type == DIAL_EVENT:
            self._handle_dial(event)
        elif event_type == BUTTON_PRESS:
            if (
                self.waiting_second_click
                and time.ticks_diff(time.ticks_ms(), self.last_click_ms)
                < KEYBOARD_DOUBLE_PRESS_MS
            ):
                self.waiting_second_click = False
                self._update_case()
            else:
                self.waiting_second_click = True
                self.last_click_ms = time.ticks_ms()

    def _handle_dial(self, event):
        try:
            movement = int(event)
        except (TypeError, ValueError):
            return
        if movement:
            self.current = (self.current + movement) % self.alphabet_length
            self.dirty |= _DIRTY_KEYS

    def _update_case(self):
        selected = self.alphabet[self.current]
        self.upper_case = not self.upper_case
        self.alphabet = ALPHABET_UPPER if self.upper_case else ALPHABET_LOWER
        self.alphabet_length = len(self.alphabet)
        try:
            self.current = self.alphabet.index(selected.swapcase())
        except ValueError:
            try:
                self.current = self.alphabet.index(selected)
            except ValueError:
                self.current = 0
        self.dirty |= _DIRTY_KEYS
        print("KEYBOARD|case|{}".format("upper" if self.upper_case else "lower"))

    def _handle_button(self):
        character = self.alphabet[self.current]
        if character == "~":
            del self.return_buffer[:]
            self.return_buffer.extend(self.get_text().encode("utf-8"))
            print("KEYBOARD|submit|{}".format(self.text_length))
            self.app.state_manager.replace_state(self.last_state)
            return
        if character == "<":
            self.backspace()
            return
        if self.text_length >= KEYBOARD_TEXT_LIMIT:
            return
        self.text_buffer.append(" " if character == "_" else character)
        self.text_length = len(self.text_buffer)
        self.dirty |= _DIRTY_TEXT

    def draw(self, force=False):
        if self.dirty == 0:
            return
        now = time.ticks_ms()
        if not force and time.ticks_diff(now, self.last_frame) < KEYBOARD_FRAME_INTERVAL_MS:
            return
        dirty = self.dirty
        if dirty & _DIRTY_TEXT:
            self._draw_text()
        if dirty & _DIRTY_KEYS:
            self._draw_keys()
        self.dirty = 0
        self.last_frame = now

    def _draw_keys(self):
        display = self.display
        display.fill_rect(
            0,
            KEYBOARD_KEY_Y - KEYBOARD_TEXT_BOX_INSET,
            SCREEN_WIDTH,
            KEYBOARD_KEY_HEIGHT + KEYBOARD_TEXT_BOX_INSET * 2,
            COLOR_BACKGROUND,
        )
        for index in range(KEYBOARD_VISIBLE_KEYS):
            x = KEYBOARD_KEY_X[index]
            selected = index == KEYBOARD_SELECTED_KEY_INDEX
            background = COLOR_SELECTED_BG if selected else COLOR_SURFACE
            foreground = COLOR_SELECTED_TEXT if selected else COLOR_TEXT
            display.fill_rect(
                x, KEYBOARD_KEY_Y, KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_HEIGHT, background
            )
            display.rect(
                x,
                KEYBOARD_KEY_Y,
                KEYBOARD_KEY_WIDTH,
                KEYBOARD_KEY_HEIGHT,
                COLOR_PRIMARY if selected else COLOR_BORDER,
            )
            alphabet_index = (
                self.current + index - KEYBOARD_SELECTED_KEY_INDEX
            ) % self.alphabet_length
            character = self.alphabet[alphabet_index]
            char_x = x + (KEYBOARD_KEY_WIDTH - display.measure_text(character)) // 2
            display.text(
                character,
                char_x,
                KEYBOARD_KEY_Y + KEYBOARD_KEY_TEXT_Y_OFFSET,
                foreground,
                background,
            )

    def _draw_text(self):
        display = self.display
        display.fill_rect(
            KEYBOARD_TEXT_X,
            KEYBOARD_TEXT_Y,
            KEYBOARD_TEXT_COLUMNS * display.font_width,
            KEYBOARD_TEXT_ROWS * KEYBOARD_TEXT_LINE_HEIGHT,
            COLOR_SURFACE,
        )
        for index, character in enumerate(self.text_buffer):
            row = index // KEYBOARD_TEXT_COLUMNS
            column = index - row * KEYBOARD_TEXT_COLUMNS
            display.text(
                character,
                KEYBOARD_TEXT_X + column * display.font_width,
                KEYBOARD_TEXT_Y + row * KEYBOARD_TEXT_LINE_HEIGHT,
                COLOR_TEXT,
                COLOR_SURFACE,
            )

    def backspace(self):
        if self.text_buffer:
            self.text_buffer.pop()
            self.text_length = len(self.text_buffer)
            self.dirty |= _DIRTY_TEXT

    def clear_text(self):
        del self.text_buffer[:]
        self.text_length = 0
        self.dirty |= _DIRTY_TEXT

    def get_text(self):
        return "".join(self.text_buffer)

    def is_full(self):
        return self.text_length >= KEYBOARD_TEXT_LIMIT
