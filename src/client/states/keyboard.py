import time
from micropython import const
import struct

from config import DIAL_EVENT, BUTTON_PRESS
from config.ui_config import (
    COLOR_BACKGROUND, COLOR_BORDER, COLOR_PRIMARY, COLOR_SELECTED_BG,
    COLOR_SELECTED_TEXT, COLOR_SURFACE, COLOR_TEXT, COLOR_TEXT_MUTED,
    CONTENT_TOP, MENU_ROW_GAP, SCREEN_MARGIN, SCREEN_WIDTH,
)

_UPPER_CASE = const(1)
_LOWER_CASE = const(2)

_DIRTY_KEYS = const(1)
_DIRTY_TEXT = const(2)

_SELECTED_KEY = const(2)
_VISIBLE_KEYS = const(5)

_KEY_Y = const(236)
_KEY_WIDTH = const(40)
_KEY_HEIGHT = const(40)

_TEXT_X = const(16)
_TEXT_Y = const(88)
_TEXT_COLUMNS = const(26)
_TEXT_ROWS = const(2)
_TEXT_LIMIT = const(28)

_FRAME_INTERVAL_MS = const(25)
_BUTTON_DEBOUNCE_MS = const(400)
ALPHABET_ = "abcdefghijklmnopqrstuvwxyz1234567890_<~"
ALPHABET_SHIFT_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,!?@£$&*()#:;^%-+_|\\/<>"

RETURN_POINTER = "return-kb-data.tmp"



class Keyboard:
    KEY_X = (12, 56, 100, 144, 188)

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

        self.text_buffer = bytearray(_TEXT_LIMIT)
        self.text_length: int = 0

        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        
        self.last_click_ms = time.ticks_ms()
        self.waiting_second_click = False
        self.case_dirty = _UPPER_CASE | _LOWER_CASE
        

        now = time.ticks_ms()

        self.last_frame = time.ticks_add(
            now,
            -_FRAME_INTERVAL_MS,
        )

        self.last_button = time.ticks_add(
            now,
            -_BUTTON_DEBOUNCE_MS,
        )

    def enter_state(self):
        display = self.display
        display.begin_screen("Keyboard", "Rotate")
        display.draw_text_block(
            self.kb_text_,
            SCREEN_MARGIN,
            CONTENT_TOP + 8,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=COLOR_TEXT_MUTED,
            max_lines=1,
            bottom=_TEXT_Y,
        )
        display.fill_rect(
            _TEXT_X - 4, _TEXT_Y - 4,
            SCREEN_WIDTH - (_TEXT_X - 4) * 2, 76,
            COLOR_SURFACE,
        )
        display.rect(
            _TEXT_X - 4, _TEXT_Y - 4,
            SCREEN_WIDTH - (_TEXT_X - 4) * 2, 76,
            COLOR_BORDER,
        )
        display.text("< Backspace    _ Space", SCREEN_MARGIN, 176, COLOR_TEXT_MUTED)
        display.text("Double press changes case", SCREEN_MARGIN, 200, COLOR_TEXT_MUTED)
        display.text("~ Enter", SCREEN_MARGIN, 220, COLOR_TEXT_MUTED)
        display.draw_nav_bar(
            left="Rotate", center="Case", right="Press",
            left_icon="action_scroll", center_icon="nav_change_edit",
            right_icon="nav_enter_select",
        )
        self.case_dirty |= _LOWER_CASE
        self.wait_buffer = 0
        
        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        self.draw(force=True)

    def exit_state(self):
        return

    def update(self):
        if time.ticks_diff(time.ticks_ms(), self.last_click_ms) > _BUTTON_DEBOUNCE_MS and self.waiting_second_click:
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
            if self.waiting_second_click and time.ticks_diff(time.ticks_ms(), self.last_click_ms) < _BUTTON_DEBOUNCE_MS:
                self.waiting_second_click = False
                self._update_case()
                self.dirty |= _DIRTY_KEYS
                self.wait_buffer = 0
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
            self.alphabet = bytes(ALPHABET_SHIFT_, 'UTF-8')
            self.case_dirty &= ~_UPPER_CASE
            self.case_dirty |= _LOWER_CASE
            
        elif (self.case_dirty & _LOWER_CASE):
            self.alphabet = bytes(ALPHABET_, 'UTF-8')
            self.case_dirty &= ~_LOWER_CASE
            self.case_dirty |= _UPPER_CASE
        else:
            return




    def _handle_button(self):
        now = time.ticks_ms()

        self.last_button = now

        if self.text_length >= _TEXT_LIMIT:
            return

        character = self.alphabet[self.current]
        if (self.case_dirty & _UPPER_CASE):
            if character == 126:
                txt = map(ord, self.get_text())                
                self.return_buffer.extend(txt)
                
                self.app.state_manager.replace_state(self.last_state)
                return
            if character == 60:
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
            if time.ticks_diff(now, self.last_frame) < _FRAME_INTERVAL_MS:
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

        display.fill_rect(0, _KEY_Y - 4, SCREEN_WIDTH, _KEY_HEIGHT + 8, COLOR_BACKGROUND)

        for index in range(_VISIBLE_KEYS):
            x = self.KEY_X[index]

            if index == _SELECTED_KEY:
                background = COLOR_SELECTED_BG
                foreground = COLOR_SELECTED_TEXT
            else:
                background = COLOR_SURFACE
                foreground = COLOR_TEXT
            display.fill_rect(x, _KEY_Y, _KEY_WIDTH, _KEY_HEIGHT, background)
            display.rect(
                x, _KEY_Y, _KEY_WIDTH, _KEY_HEIGHT,
                COLOR_PRIMARY if index == _SELECTED_KEY else COLOR_BORDER,
            )

            offset = index - _SELECTED_KEY
            alphabet_index = self.current + offset

            while alphabet_index >= self.alphabet_length:
                alphabet_index -= self.alphabet_length

            while alphabet_index < 0:
                alphabet_index += self.alphabet_length
    
            character = chr(self.alphabet[alphabet_index])
            char_x = x + (_KEY_WIDTH - display.measure_text(character)) // 2
            display.text(
                character, char_x, _KEY_Y + 12, foreground, background
            )

    def _draw_corners(self, x):
        self.display.rect(x, _KEY_Y, _KEY_WIDTH, _KEY_HEIGHT, COLOR_BORDER)

    def _draw_text(self):
        display = self.display
        display.fill_rect(
            _TEXT_X,
            _TEXT_Y,
            _TEXT_COLUMNS * display.font_width,
            _TEXT_ROWS * 20,
            COLOR_SURFACE,
        )

        for index in range(self.text_length):
            row = index // _TEXT_COLUMNS
            column = index - row * _TEXT_COLUMNS
            char_ = ' ' if chr(self.text_buffer[index]) == '_' else chr(self.text_buffer[index])
            if char_ == '<':
                self.backspace()
                return
            
            display.text(
                char_,
                _TEXT_X + column * display.font_width,
                _TEXT_Y + row * 20,
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
        return self.text_length >= _TEXT_LIMIT
