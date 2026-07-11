import time
from libraries.rotary_irq_esp import RotaryIRQ

from config.config import (
    INPUT_DEBOUNCE_MS,
)
from machine import Pin

"""
None refers to no input and False / True refer to specific actions
"""

# Removed ToggleInput base class as it was causing inefficient resource allocation.
# Dial and Button will now initialize their specific hardware directly.

class Dial:
    def __init__(self):
        self.rotary_encoder = RotaryIRQ(
            pin_num_clk=18,
            pin_num_dt=19,
            incr=1,
            range_mode=RotaryIRQ.RANGE_WRAP,
            pull_up = True,
            half_step=False,
            reverse=True,
        )
        self.rotary_encoder.set(min_val=0, max_val=1000)
        self.last_event_ms = time.ticks_ms()
        # Initialize with the current encoder value to track changes from this point
        self.last_processed_encoder_value = self.rotary_encoder.value()
        # minimum_turn is not directly used in the new logic, consider removing if not needed elsewhere
        self.minimum_turn = 10

    @property
    def event_type(self):
        return "dial"

    def event(self):
        current_encoder_value = self.rotary_encoder.value()
        print(current_encoder_value)
        _now = time.ticks_ms()

        # Calculate the difference since the last *processed* event
        difference = current_encoder_value - self.last_processed_encoder_value

        if difference == 0:
            return None  # No change in encoder value

        # Check debounce time
        if time.ticks_diff(_now, self.last_event_ms) < 1000:
            return None  # Not enough time has passed since the last event

        # If we reach here, it's a valid event
        self.last_event_ms = _now
        self.last_processed_encoder_value = current_encoder_value  # Update last processed value

        # Determine direction
        direction = 1 if difference > 0 else -1
        if difference > self.minimum_turn or difference < -self.minimum_turn: return None
        print(str(direction))
        return direction


class Button:
    def __init__(self):
        self.button_pin = Pin(
            23,
            Pin.IN,
            Pin.PULL_UP
        )
        self.input_armed_button = True
        self.last_trigger_ms_button = time.ticks_ms()

    def event(self):
        return self.read_event_button()

    @property
    def event_type(self):
        return "button"

    def read_event_button(self):
        now_ms = time.ticks_ms()
        is_pressed = (self.button_pin.value() == 0)  # True if pressed, False if not

        if not is_pressed:
            self.input_armed_button = True  # Re-arm when button is released
            return None

        # Button is pressed
        if not self.input_armed_button:
            return None  # Button is pressed but not armed (still debouncing from previous press)

        if not self._check_time_valid(self.last_trigger_ms_button, now_ms):
            return None  # Not enough time passed since last trigger

        # Valid button press
        self.input_armed_button = False  # Disarm until released
        self.last_trigger_ms_button = now_ms
        return True  # Return True for a valid press

    def _check_time_valid(self,
                          last_trig_static,
                          now_ms,
                          ):
        return time.ticks_diff(now_ms, last_trig_static) >= INPUT_DEBOUNCE_MS
