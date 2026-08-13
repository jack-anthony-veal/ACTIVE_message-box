import gc

from config.config import OLED_BORDER_HEIGHT, OLED_BORDER_WIDTH, OLED_BORDER_SCREEN
from config.config import (
    I2C_SCL_PIN,
    I2C_SDA_PIN,
    MENU_Y_AXIS,
    OLED_CHARS_PER_LINE,
    OLED_HEIGHT,
    OLED_MAX_LINES,
    OLED_TEXT_HEIGHT,
    OLED_WIDTH,
)
from libraries import sh1106
from libraries.utils.text_tools import message_from_payload, wrap_text
from machine import Pin, I2C


class OledDisplay:
    def __init__(self):
        self.width: int = OLED_BORDER_WIDTH
        self.height: int = OLED_BORDER_HEIGHT
        self.i2c_bus = I2C(
                            0,
                            scl=Pin(I2C_SCL_PIN),
                            sda=Pin(I2C_SDA_PIN),
                            freq=400000
                        )

        self.oled = sh1106.SH1106(OLED_WIDTH, OLED_HEIGHT, self.i2c_bus)

    def queue_text(self,text, x, y, c=1):
        self.oled.text(text, x, y, c)

    def draw_art(self,data=None, x_offset=0, y_offset=0, color=1):
        for index in range(0, len(data), 3):
            y = data[index] + y_offset
            x = data[index + 1] + x_offset
            length = data[index + 2]
            self.oled.hline(x, y, length, color)


    def show_error(self, art_runs, message_1="", message_2=""):
        x_ = [message_1, message_2]
        x_ = [x[:14] for x in x_]
        message_1 = x_[0]; message_2 = x_[1]
        for index in range(0, len(art_runs), 3):
            y = art_runs[index] + 0
            x = art_runs[index + 1] + 0
            length = art_runs[index + 2]
            self.oled.hline(x, y, length, 1)

        height = OLED_BORDER_HEIGHT
        width = OLED_BORDER_WIDTH
        self.oled.fill(0)
        self.oled.rect(0, 0, width, height, 1)
        self.draw_art(art_runs)
        # reserved line index 1
        self.oled.fill_rect(2, 8, width - 4, 8, 0)
        self.oled.text(str(message_1)[:14], 8, 8, 1)
        # reserved line index 4
        self.oled.fill_rect(2, 32, width - 4, 8, 0)
        self.oled.text(str(message_2)[:14], 8, 32, 1)
        self.oled.show()


    def show_queue(self):
        try:
            self.oled.show()
        except OSError:
            time.sleep_ms(5)
            self.oled.show()

    def power_on(self):
        try:
            self.oled.poweron()
            self.oled.fill(0)
        except Exception:
            gc.collect()
            raise

    def power_off(self):
        self.oled.poweroff()

    def custom_message(self,
                       data=None,
                       x_axis: int=1, y_axis: int=1,
                       fill_x_axis: int=0, fill_y_axis: int=0, fill_start_line: int=0, fill_start_x=0,
                       wrap=False, fill_all=False, max_=True, color=0
                       ):

        self.draw_art(OLED_BORDER_SCREEN)
        if fill_all and data is None: self.oled.fill(0) # Fill whole screen
        if data is None: self.oled.show(); del data; return
        if fill_all: self.oled.fill(0)

        if fill_start_line != 0 or fill_x_axis != 0 or fill_y_axis != 0: # Fill custom rect
            self.oled.fill_rect(fill_start_x, fill_start_line, fill_x_axis, fill_y_axis, color)
            self.oled.show()

        if not wrap: self.oled.text(str(data), x_axis, y_axis, 1); self.oled.show(); return

        start_line = int(round(y_axis // 8, 0)) if y_axis != 0 else 0

        if type(data) == list:
            next_line = start_line

            for preset_text in data:  # Manage list of items
                preset_text = message_from_payload(preset_text)
                next_line = self.draw_wrap_text(
                    preset_text,
                    start_line=next_line,
                    return_next_line=True,
                    x_axis=x_axis,
                    max_=max_
                )
            self.oled.show()
            return

            # Converts the data to string
        data = message_from_payload(data) if type(data) != str else data
        self.draw_wrap_text(data,start_line=start_line, x_axis=x_axis, color=1,max_=max_); self.oled.show()

        del data, start_line, x_axis, y_axis, fill_x_axis, fill_y_axis, fill_start_line
        return

    def draw_wrap_text(self, message, return_next_line=False, start_line=0, x_axis=0, color=1, max_=True):
        message = str(message)
        line_limit = max(0, OLED_MAX_LINES - start_line) if max_ else None
        if line_limit == 0:
            return start_line if return_next_line else None
        wrapped_lines = wrap_text(message, OLED_CHARS_PER_LINE, max_lines=line_limit)

        for line_index, line_text in enumerate(wrapped_lines): # Limit height
            self.oled.text(str(line_text), x_axis, (start_line+line_index)*OLED_TEXT_HEIGHT, 1)

        if return_next_line:
            return start_line + len(wrapped_lines)



    def clear_message_area(self):
        self.oled.fill_rect(0, 0, self.width, MENU_Y_AXIS, 0)
        self.oled.show()

    def clear_menu_area(self):
        self.oled.fill_rect(0, MENU_Y_AXIS, self.width, OLED_TEXT_HEIGHT, 0)
        self.oled.show()
