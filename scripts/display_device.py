from machine import Pin, I2C

import sh1106

from config import (
    I2C_SCL_PIN,
    I2C_SDA_PIN,
    MENU_Y,
    OLED_CHARS_PER_LINE,
    OLED_HEIGHT,
    OLED_MAX_LINES,
    OLED_TEXT_HEIGHT,
    OLED_WIDTH,
)
from text_tools import message_from_payload, wrap_text


class OledDisplay:
    def __init__(self):
        self.width: int = OLED_WIDTH
        self.height: int = OLED_HEIGHT

        self.i2c_bus = I2C(
            0,
            scl=Pin(I2C_SCL_PIN),
            sda=Pin(I2C_SDA_PIN),
            freq=100000
        )

        self.oled = sh1106.SH1106(self.width, self.height, self.i2c_bus)

        self.text_height: int = OLED_TEXT_HEIGHT
        self.chars_per_line: int = OLED_CHARS_PER_LINE
        self.max_lines = OLED_MAX_LINES

        self.power_enabled: bool = False
        self.menu_y = MENU_Y


    def __repr__(self):
        return str([self.power_enabled, self.text_height, self.chars_per_line, self.max_lines, self.menu_y])

    def __str__(self):
        return str(self.power_enabled)

    def power_on(self):
        if not self.power_enabled:
            self.power_enabled = True
            self.oled.poweron()

            self.oled.fill(0)

    def power_off(self):
        self.oled.poweroff()

    def custom_message(self,
                       data=None,
                       x_axis=0, y_axis=0.0, color=1,
                       fill_x_axis=0, fill_y_axis=0, fill_start_line=0,
                       wrap=False, fill_all=False
                       ):

        if 0 not in [fill_start_line, fill_x_axis, fill_y_axis]: # Fill custom rect
            self.oled.fill_rect(0, fill_start_line, fill_x_axis, fill_y_axis, 0)

        if fill_all or data is None: self.oled.fill(0) # Fill whole screen
        self.oled.show()
        if data is None: return # Return after fill

        start_line = round(y_axis / 8) if y_axis != 0 else 0

        if not wrap:  # Reduces process time for non-wrap text
            self.oled.text(str(data), x_axis, y_axis, 1)
            self.oled.show()
            return

            # Handles list elements for presets
        if type(data) == list:
            next_line = start_line
            for preset_text in data:  # Manage list of items
                preset_text = message_from_payload(preset_text)
                next_line = self.draw_wrap_text(
                    preset_text,
                    start_line=next_line,
                    return_next_line=True,
                    x_axis=x_axis,
                )
                print(next_line)

            self.oled.show()
            return

            # Converts the data to string
        message_text = message_from_payload(data)

        # Draws
        self.draw_wrap_text(message_text,start_line=start_line, x_axis=x_axis, color=color)
        self.oled.show()

    def draw_wrap_text(self, message, return_next_line=False, start_line=0, x_axis=0, color=1):

        line_limit = self.max_lines - start_line
        wrapped_lines = wrap_text(message, self.chars_per_line, max_lines=line_limit)

        for line_index, line_text in enumerate(wrapped_lines): # Limit height
            if line_index > self.max_lines: break
            self.oled.text(line_text, x_axis, (start_line+line_index)*8, color)

        if return_next_line:
            return start_line + len(wrapped_lines) # Give next line so wrap can occur



    def clear_message_area(self):
        self.oled.fill_rect(0, 0, self.width, self.menu_y, 0)

    def clear_menu_area(self):
        self.oled.fill_rect(0, self.menu_y, self.width, self.text_height, 0)

    def show_menu(self, menu_text):
        self.clear_menu_area()
        self.oled.text(menu_text[:self.chars_per_line], 0, self.menu_y, 1)
        self.oled.show()
