import time
from micropython import const

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, COLOR_BACKGROUND, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_SELECTED_BG, COLOR_SELECTED_TEXT, COLOR_SURFACE, COLOR_TEXT,
    COLOR_TEXT_MUTED, CONTENT_TOP, DIAL_EVENT, KEYBOARD_BACKSPACE_CHARACTER,
    KEYBOARD_BACKSPACE_HELP_Y, KEYBOARD_CASE_HELP_Y, KEYBOARD_DOUBLE_PRESS_MS,
    KEYBOARD_ENTER_CHARACTER, KEYBOARD_ENTER_HELP_Y,
    KEYBOARD_FRAME_INTERVAL_MS, KEYBOARD_KEY_HEIGHT, KEYBOARD_KEY_TEXT_Y_OFFSET,
    KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_X, KEYBOARD_KEY_Y,
    KEYBOARD_SELECTED_KEY_INDEX, KEYBOARD_TEXT_BOX_HEIGHT,
    KEYBOARD_TEXT_BOX_INSET, KEYBOARD_TEXT_COLUMNS, KEYBOARD_TEXT_LIMIT,
    KEYBOARD_TEXT_LINE_HEIGHT, KEYBOARD_TEXT_ROWS, KEYBOARD_TEXT_X,
    KEYBOARD_TEXT_Y, KEYBOARD_VISIBLE_KEYS, SCREEN_MARGIN, SCREEN_WIDTH,
    SPACE_SM,
)

_UPPER_CASE = const(1)
_LOWER_CASE = const(2)

_DIRTY_KEYS = const(1)
_DIRTY_TEXT = const(2)

ALPHABET_ = "abcdefghijklmnopqrstuvwxyz1234567890_<~"
ALPHABET_SHIFT_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,!?@£$&*()#:;^%-+_|\\/<>"


class Keyboard:
    def __init__(self, app, last_state, return_buffer, kb_text="Begin Typing"):
        self.app = app
        self.display = app.display
        self.last_state = last_state
        self.return_buffer = return_buffer
        self.kb_text_ = kb_text

        alphabet = ALPHABET_

        if not isinstance(alphabet, str):
            alphabet = "".join(alphabet)

        if not alphabet:
            raise ValueError("ALPHABET_ cannot be empty")

        try:
            self.alphabet = alphabet.encode("ascii")
        except:
            self.alphabet = bytes(alphabet)

        self.alphabet_length = len(self.alphabet)

        self.current = 0

        self.text_buffer = bytearray(KEYBOARD_TEXT_LIMIT)
        self.text_length: int = 0

        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        
        self.last_click_ms = time.ticks_ms()
        self.waiting_second_click = False
        self.case_dirty = _UPPER_CASE | _LOWER_CASE
        

        now = time.ticks_ms()

        self.last_frame = time.ticks_add(
            now,
            -KEYBOARD_FRAME_INTERVAL_MS,
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
            SCREEN_WIDTH
            - (KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET) * 2,
            KEYBOARD_TEXT_BOX_HEIGHT,
            COLOR_SURFACE,
        )
        display.rect(
            KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET,
            KEYBOARD_TEXT_Y - KEYBOARD_TEXT_BOX_INSET,
            SCREEN_WIDTH
            - (KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET) * 2,
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
        display.text(
            "~ Enter", SCREEN_MARGIN, KEYBOARD_ENTER_HELP_Y, COLOR_TEXT_MUTED
        )
        display.draw_nav_bar(
            left="Rotate", center="Case", right="Press",
            left_icon=ICONS["action"]["scroll"],
            center_icon=ICONS["navigation"]["edit"],
            right_icon=ICONS["navigation"]["select"],
        )
        self.case_dirty |= _LOWER_CASE
        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        self.draw(force=True)

    def exit_state(self):
        return

    def update(self):
        if (
            time.ticks_diff(time.ticks_ms(), self.last_click_ms)
            > KEYBOARD_DOUBLE_PRESS_MS
            and self.waiting_second_click
        ):
            self.waiting_second_click = False
            self._handle_button()
            
        self.draw()

    def handle_input(self, event, type_):
        if event is None:
            return

        if type_ == DIAL_EVENT:
            self._handle_dial(event)
            return

        if type_ == BUTTON_PRESS:
            if (
                self.waiting_second_click
                and time.ticks_diff(time.ticks_ms(), self.last_click_ms)
                < KEYBOARD_DOUBLE_PRESS_MS
            ):
                self.waiting_second_click = False
                self._update_case()
                self.dirty |= _DIRTY_KEYS
            else:
                self.waiting_second_click = True
                self.last_click_ms = time.ticks_ms()
                return

    def _handle_dial(self, event):
        try:
            movement = int(event)
        except (TypeError, ValueError):
            return

        if movement == 0:
            return

        self.current += movement

        while self.current >= self.alphabet_length:
            self.current -= self.alphabet_length

        while self.current < 0:
            self.current += self.alphabet_length

        self.dirty |= _DIRTY_KEYS
        self.draw()
        
        
        
        
    def _update_case(self):
        if (self.case_dirty & _UPPER_CASE):
            self.alphabet = ALPHABET_SHIFT_.encode("utf-8")
            self.case_dirty &= ~_UPPER_CASE
            self.case_dirty |= _LOWER_CASE
            
        elif (self.case_dirty & _LOWER_CASE):
            self.alphabet = ALPHABET_.encode("utf-8")
            self.case_dirty &= ~_LOWER_CASE
            self.case_dirty |= _UPPER_CASE
        else:
            return




    def _handle_button(self):
        if self.text_length >= KEYBOARD_TEXT_LIMIT:
            return

        character = self.alphabet[self.current]
        if (self.case_dirty & _UPPER_CASE):
            if character == KEYBOARD_ENTER_CHARACTER:
                txt = map(ord, self.get_text())                
                self.return_buffer.extend(txt)
                
                self.app.state_manager.replace_state(self.last_state)
                return
            if character == KEYBOARD_BACKSPACE_CHARACTER:
                self.backspace()
                return

        try:
            self.text_buffer[self.text_length] = ord(character)
        except:
            self.text_buffer[self.text_length] = character
            
        self.text_length = int(self.text_length) + 1

        self.dirty |= _DIRTY_TEXT

        self.draw(force=True)

    def draw(self, force=False):
        if self.dirty == 0:
            return

        now = time.ticks_ms()

        if not force:
            if (
                time.ticks_diff(now, self.last_frame)
                < KEYBOARD_FRAME_INTERVAL_MS
            ):
                return

        dirty = self.dirty

        if dirty & _DIRTY_TEXT:
            self._draw_text()

        if dirty & _DIRTY_KEYS:
            self._draw_keys()

        self.dirty = 0
        self.last_frame = time.ticks_ms()

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

            if index == KEYBOARD_SELECTED_KEY_INDEX:
                background = COLOR_SELECTED_BG
                foreground = COLOR_SELECTED_TEXT
            else:
                background = COLOR_SURFACE
                foreground = COLOR_TEXT
            display.fill_rect(
                x, KEYBOARD_KEY_Y,
                KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_HEIGHT,
                background,
            )
            display.rect(
                x, KEYBOARD_KEY_Y,
                KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_HEIGHT,
                COLOR_PRIMARY
                if index == KEYBOARD_SELECTED_KEY_INDEX
                else COLOR_BORDER,
            )

            offset = index - KEYBOARD_SELECTED_KEY_INDEX
            alphabet_index = self.current + offset

            while alphabet_index >= self.alphabet_length:
                alphabet_index -= self.alphabet_length

            while alphabet_index < 0:
                alphabet_index += self.alphabet_length
    
            character = chr(self.alphabet[alphabet_index])
            char_x = x + (
                KEYBOARD_KEY_WIDTH - display.measure_text(character)
            ) // 2
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

        for index in range(self.text_length):
            row = index // KEYBOARD_TEXT_COLUMNS
            column = index - row * KEYBOARD_TEXT_COLUMNS
            char_ = ' ' if chr(self.text_buffer[index]) == '_' else chr(self.text_buffer[index])
            if char_ == '<':
                self.backspace()
                return
            
            display.text(
                char_,
                KEYBOARD_TEXT_X + column * display.font_width,
                KEYBOARD_TEXT_Y + row * KEYBOARD_TEXT_LINE_HEIGHT,
                COLOR_TEXT,
                COLOR_SURFACE,
            )

    def backspace(self):
        if self.text_length == 0:
            return

        self.text_length -= 1
        self.text_buffer[self.text_length] = 0

        self.dirty |= _DIRTY_TEXT
        self.draw(force=True)

    def clear_text(self):
        if self.text_length == 0:
            return

        self.text_length = 0

        self.dirty |= _DIRTY_TEXT
        self.draw(force=True)

    def get_text(self):
        return bytes(
            self.text_buffer[:self.text_length]
        ).decode("ascii")

    def is_full(self):
        return self.text_length >= KEYBOARD_TEXT_LIMIT
