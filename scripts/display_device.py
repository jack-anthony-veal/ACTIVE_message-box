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
                       x_axis=0, y_axis=0, color=1,
                       fill_x_axis=0, fill_y_axis=0, fill_start_line=0,
                       wrap=False, fill_all=False
                       ):

        if 0 not in [fill_start_line, fill_x_axis, fill_y_axis]: # Fill custom rect
            self.oled.fill_rect(0, fill_start_line, fill_x_axis, fill_y_axis, 0)

        if fill_all and data is None: self.oled.fill(0) # Fill whole screen
        if data is None: return # Return after fill

        if type(data) == list and wrap:
            next_line = y_axis

            for preset_text in data:  # Manage list of items
                preset_text = message_from_payload(preset_text) # Turns to str
                next_line = self.draw_wrapped_text( # Draws lists properly
                    preset_text,
                    start_line=next_line,
                    return_next_line=True,
                    x_axis=x_axis,
                    color=color
                )
        else: data = message_from_payload(data)

        if wrap and type(data) is str:
            data = wrap_text(data)
            for line, data_text in enumerate(data):
                if line >= self.max_lines: break # Only show max lines
                self.oled.text(data_text, x_axis, (line*8)+y_axis, color) # Parse the list to fit screen

        else: raise "TROUBLE DISPLAYING LN: in display.py" # TODO: Add exception handler

        self.oled.show()


    def draw_wrapped_text(self, message, return_next_line=False, start_line=0, x_axis=0, color=1):
        line_limit = self.max_lines - start_line
        wrapped_lines = wrap_text(message, self.chars_per_line, max_lines=line_limit)

        for line_index, line_text in enumerate(wrapped_lines): # Limit height
            y_position = (start_line + line_index) * self.text_height
            self.oled.text(line_text, x_axis, y_position, color)

        self.oled.show()

        if return_next_line: return start_line + len(wrapped_lines) # Give next line so wrap can occur
        else: return None

    def clear_message_area(self):
        self.oled.fill_rect(0, 0, self.width, self.menu_y, 0)

    def clear_menu_area(self):
        self.oled.fill_rect(0, self.menu_y, self.width, self.text_height, 0)

    def show_menu(self, menu_text):
        self.clear_menu_area()
        self.oled.text(menu_text[:self.chars_per_line], 0, self.menu_y, 1)
        self.oled.show()
