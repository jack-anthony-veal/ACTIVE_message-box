import time
from libraries.rotary_irq_esp import RotaryIRQ

from config.config import (
    BUTTON_DEBOUNCE_MS, BUTTON_PIN, BUTTON_PRESS, DIAL_CLK_PIN, DIAL_DT_PIN,
    DIAL_EVENT, ENCODER_EVENT_DEBOUNCE_MS, ENCODER_INCREMENT,
    ENCODER_MAX_STEP_DELTA, ENCODER_MAX_VALUE, ENCODER_MIN_STEP_DELTA,
    ENCODER_MIN_VALUE, ENCODER_RANGE_SIZE, ENCODER_WRAP_THRESHOLD,
    LEFT_DIAL, RIGHT_DIAL, WAKE_PIN,
)
from machine import Pin


class OnSwitch:
    """Compatibility wrapper for the configured deep-sleep wake input."""

    def __init__(self):
        self.wake_up_pins = [Pin(WAKE_PIN, Pin.IN, Pin.PULL_UP)]


class Dial:
    def __init__(self):
        self.rotary_encoder = RotaryIRQ(
            pin_num_clk=DIAL_CLK_PIN,
            pin_num_dt=DIAL_DT_PIN,
            incr=ENCODER_INCREMENT,
            range_mode=RotaryIRQ.RANGE_WRAP,
            pull_up=True,
            half_step=False,
            reverse=True,
        )
        self.rotary_encoder.set(
            min_val=ENCODER_MIN_VALUE,
            max_val=ENCODER_MAX_VALUE,
        )
        self.last_event_ms = time.ticks_ms()
        self.last_processed_encoder_value = self.rotary_encoder.value()
        self.minimum_step_delta = ENCODER_MIN_STEP_DELTA
        self.maximum_step_delta = ENCODER_MAX_STEP_DELTA

    @property
    def event_type(self):
        return DIAL_EVENT

    def event(self):
        current_encoder_value = self.rotary_encoder.value()
        now_ms = time.ticks_ms()
        difference = current_encoder_value - self.last_processed_encoder_value

        if difference == 0:
            return None

        if (
            time.ticks_diff(now_ms, self.last_event_ms)
            < ENCODER_EVENT_DEBOUNCE_MS
        ):
            return None

        self.last_event_ms = now_ms
        self.last_processed_encoder_value = current_encoder_value

        if difference > ENCODER_WRAP_THRESHOLD:
            difference -= ENCODER_RANGE_SIZE
        elif difference < -ENCODER_WRAP_THRESHOLD:
            difference += ENCODER_RANGE_SIZE

        direction = RIGHT_DIAL if difference > 0 else LEFT_DIAL
        if abs(difference) > self.maximum_step_delta:
            return None
        if abs(difference) < self.minimum_step_delta:
            return None

        return direction


class Button:
    def __init__(self):
        self.button_pin = Pin(
            BUTTON_PIN,
            Pin.IN,
            Pin.PULL_UP
        )
        self.input_armed_button = True
        self.last_trigger_ms_button = time.ticks_ms()
        self.event_t = BUTTON_PRESS

    def event(self):
        return self.read_event_button()

    @property
    def event_type(self):
        return self.event_t

    def read_event_button(self):
        is_pressed = self.button_pin.value() == 0
        if not is_pressed:
            self.input_armed_button = True
            return None

        now_ms = time.ticks_ms()
        if (
            not self._check_time_valid(self.last_trigger_ms_button, now_ms)
            or not self.input_armed_button
        ):
            return None

        self.input_armed_button = False
        self.last_trigger_ms_button = now_ms
        return True

    def _check_time_valid(self, last_trig_static, now_ms):
        return time.ticks_diff(now_ms, last_trig_static) >= BUTTON_DEBOUNCE_MS
