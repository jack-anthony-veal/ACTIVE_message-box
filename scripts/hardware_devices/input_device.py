import time

from config.config import (
    INPUT_DEBOUNCE_MS,
    LEFT_PIN,
    RIGHT_PIN,
    RIGHT_PIN_CHECK,
    LEFT_PIN_CHECK
)
from machine import Pin

"""
None refers to no input and False / True refer to specific actions
"""


class ToggleInput:
    def __init__(self):
        self.left_pin = Pin(LEFT_PIN,
                            Pin.IN,
                            Pin.PULL_UP
                            )
        self.right_pin = Pin(RIGHT_PIN,
                             Pin.IN,
                             Pin.PULL_UP
                             )
        self.button_pin = Pin(12,  # Ammend to have a constant
                              Pin.IN,
                              Pin.PULL_UP)

        self.input_armed_switch = True
        self.last_trigger_ms_switch = time.ticks_ms()

        self.input_armed_button = True
        self.last_trigger_ms_button = time.ticks_ms()

    def read_event_button(self):
        now_ms = time.ticks_ms()
        is_pressed = True if self.button_pin.value() == 0 else None  # returns True if pressed

        if not is_pressed:
            self.input_armed_button = True
            return None

        if not self.input_armed_button:
            return None

        if not self.check_time_valid(self.last_trigger_ms_button, now_ms):
            return None

        print(str(is_pressed))
        self.input_armed_button = False
        self.last_trigger_ms_button = now_ms
        if is_pressed: return True
        return None

    def read_position_switch(self):
        if self.left_pin.value() == 0:
            return LEFT_PIN_CHECK

        if self.right_pin.value() == 0:
            return RIGHT_PIN_CHECK

        return None

    def read_event_switch(self):
        now_ms = time.ticks_ms()
        input_position = self.read_position_switch()

        if input_position is None:  # Arm to allow double use
            self.input_armed_switch = True
            return None

        if not self.input_armed_switch:  # Disallow spamming
            return None

        if not self.check_time_valid(self.last_trigger_ms_switch, now_ms):  # Allow double use & prevent spam
            return None

        print("pressed switch")
        self.input_armed_switch = False
        self.last_trigger_ms_switch = now_ms
        return input_position


    def switch(self):
        return self.read_event_switch()

    def button(self):
        return self.read_event_button()

    def check_time_valid(self,
                         last_trig_static,
                         now_ms=None,
                         ):

        if now_ms is None:
            now_ms = time.ticks_ms()

        if time.ticks_diff(now_ms, last_trig_static) < INPUT_DEBOUNCE_MS:
            return False
        else:
            return True
