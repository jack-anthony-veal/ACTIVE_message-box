import time
from micropython import const
import struct

from config import (
    DIAL_EVENT,
    KEYBOARD_SCREEN,
    KEY_POS,
    BUTTON_PRESS,
)

_UPPER_CASE = const(1)
_LOWER_CASE = const(2)

_DIRTY_KEYS = const(1)
_DIRTY_TEXT = const(2)

_SELECTED_KEY = const(2)
_VISIBLE_KEYS = const(5)

_KEY_Y = const(55)
_KEY_WIDTH = const(22)
_KEY_HEIGHT = const(9)

_TEXT_X = const(8)
_TEXT_Y = const(20)
_TEXT_COLUMNS = const(14)
_TEXT_ROWS = const(4)
_TEXT_LIMIT = const(56)

_FRAME_INTERVAL_MS = const(25)
_BUTTON_DEBOUNCE_MS = const(400)
ALPHABET_ = "abcdefghijklmnopqrstuvwxyz1234567890_<"
ALPHABET_SHIFT_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,!?@£$&*()#~:;^%-+_|\/"

RETURN_POINTER = "return-kb-data.tmp"



class Keyboard:
    KEY_X = (1, 27, 53, 79, 105)

    def __init__(self, app, last_state):
        self.app = app
        self.display = app.display
        self.oled = app.display.oled
        self.last_state = last_state

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

        # Fixed-size typed-text buffer.
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
        self.oled.fill(0)

        self.oled.text(
            "on-screen-kb",
            0,
            0,
            1,
        )

        self.display.draw_art(
            data=KEYBOARD_SCREEN,
        )
        self.case_dirty |= _LOWER_CASE
        self.wait_buffer = 0
        
        self.dirty = _DIRTY_KEYS | _DIRTY_TEXT
        self.draw(force=True)

    def exit_state(self):
        RETURN_POINTER = self.text_buffer
        with open("../return-kb-data.tmp", "w") as return_file:
            return_file.writelines(self.get_text())
            return_file.close()
            
        self.app.state_manager.replace_state(self.last_state(kb_data=True))

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

        # Avoid modulo for the normal single-step encoder case.
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
        
            # ASCII "<" acts as backspace.
        if character == 60:
            self.backspace()
            return

        # Preserve the previous behaviour: only insert letters.

        try:
            self.text_buffer[self.text_length] = ord(character)
        except:
            self.text_buffer[self.text_length] = character
            
        self.text_length = int(self.text_length) + 1

        self.dirty |= _DIRTY_TEXT

        # A button press should appear immediately.
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

        self._show()

        self.dirty = 0
        self.last_frame = time.ticks_ms()

    def _draw_keys(self):
        oled = self.oled
        fill_rect = oled.fill_rect
        text = oled.text

        # Clear only the keyboard area.
        fill_rect(
            0,
            54,
            128,
            10,
            0,
        )

        for index in range(_VISIBLE_KEYS):
            x = self.KEY_X[index]

            if index == _SELECTED_KEY:
                fill_rect(
                    x,
                    _KEY_Y,
                    _KEY_WIDTH,
                    _KEY_HEIGHT,
                    1,
                )
            else:
                self._draw_corners(x)

            offset = index - _SELECTED_KEY
            alphabet_index = self.current + offset

            while alphabet_index >= self.alphabet_length:
                alphabet_index -= self.alphabet_length

            while alphabet_index < 0:
                alphabet_index += self.alphabet_length
    
            character = chr(self.alphabet[alphabet_index])
            color = 0 if index == _SELECTED_KEY else 1

            text(
                character,
                KEY_POS[index][0],
                KEY_POS[index][1],
                color,
            )

    def _draw_corners(self, x):
        oled = self.oled
        hline = oled.hline
        vline = oled.vline

        y = _KEY_Y
        right = x + _KEY_WIDTH - 1
        bottom = y + _KEY_HEIGHT - 1
        size = 4

        hline(x, y, size, 1)
        vline(x, y, size, 1)

        hline(right - size + 1, y, size, 1)
        vline(right, y, size, 1)

        hline(x, bottom, size, 1)
        vline(x, bottom - size + 1, size, 1)

        hline(right - size + 1, bottom, size, 1)
        vline(right, bottom - size + 1, size, 1)

    def _draw_text(self):
        oled = self.oled

        oled.fill_rect(
            _TEXT_X,
            _TEXT_Y,
            _TEXT_COLUMNS * 8,
            _TEXT_ROWS * 8,
            0,
        )

        for index in range(self.text_length):
            row = index // _TEXT_COLUMNS
            column = index - row * _TEXT_COLUMNS
            char_ = ' ' if chr(self.text_buffer[index]) == '_' else chr(self.text_buffer[index])
            if char_ == '<':
                self.backspace()
                return
            
            oled.text(
                char_,
                _TEXT_X + column * 8,
                _TEXT_Y + row * 8,
                1,
            )

    def _show(self):
        try:
            self.oled.show()
        except OSError:
            time.sleep_ms(5)
            self.oled.show()

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