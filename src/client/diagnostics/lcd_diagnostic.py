import gc
import time

from config.ui_config import (
    COLOR_BACKGROUND, COLOR_BORDER, COLOR_PRIMARY, COLOR_TEXT,
    CONTENT_BOTTOM, CONTENT_TOP, SCREEN_HEIGHT, SCREEN_MARGIN, SCREEN_WIDTH,
    rgb565,
)
from hardware_devices.display_device import Display


def wait(milliseconds=2500):
    time.sleep_ms(milliseconds)


def basic_initialisation(display):
    print("LCD_DIAGNOSTIC basic_initialisation")
    display.fill(COLOR_BACKGROUND)
    display.text("ST7789 initialised", 40, 152, COLOR_TEXT, COLOR_BACKGROUND)
    wait()


def primary_colours(display):
    print("LCD_DIAGNOSTIC primary_colours")
    colours = (
        ("RED", rgb565(255, 0, 0)),
        ("GREEN", rgb565(0, 255, 0)),
        ("BLUE", rgb565(0, 0, 255)),
        ("WHITE", rgb565(255, 255, 255)),
        ("BLACK", rgb565(0, 0, 0)),
        ("CYAN", rgb565(0, 255, 255)),
        ("MAGENTA", rgb565(255, 0, 255)),
        ("YELLOW", rgb565(255, 255, 0)),
    )
    for index, item in enumerate(colours):
        label, colour = item
        x = (index % 2) * 120
        y = (index // 2) * 80
        display.fill_rect(x, y, 120, 80, colour)
        foreground = rgb565(0, 0, 0) if label in ("WHITE", "CYAN", "YELLOW") else rgb565(255, 255, 255)
        display.text(label, x + 12, y + 32, foreground, colour)
    wait(4000)


def orientation_and_offsets(display):
    print("LCD_DIAGNOSTIC orientation_and_offsets")
    display.fill(COLOR_BACKGROUND)
    display.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rgb565(255, 255, 255))
    display.fill_rect(1, 1, 10, 10, rgb565(255, 0, 0))
    display.fill_rect(SCREEN_WIDTH - 11, 1, 10, 10, rgb565(0, 255, 0))
    display.fill_rect(1, SCREEN_HEIGHT - 11, 10, 10, rgb565(0, 0, 255))
    display.fill_rect(SCREEN_WIDTH - 11, SCREEN_HEIGHT - 11, 10, 10, rgb565(255, 255, 0))
    display.vline(120, 0, SCREEN_HEIGHT, rgb565(0, 255, 255))
    display.hline(0, 160, SCREEN_WIDTH, rgb565(255, 0, 255))
    display.text("TOP", 104, 16, COLOR_TEXT, COLOR_BACKGROUND)
    display.text("BOTTOM", 92, 288, COLOR_TEXT, COLOR_BACKGROUND)
    display.text("L", 12, 152, COLOR_TEXT, COLOR_BACKGROUND)
    display.text("R", 220, 152, COLOR_TEXT, COLOR_BACKGROUND)
    wait(5000)


def primitives(display):
    print("LCD_DIAGNOSTIC primitives")
    display.fill(COLOR_BACKGROUND)
    display.pixel(12, 68, COLOR_TEXT)
    display.hline(12, 88, 216, rgb565(255, 0, 0))
    display.vline(32, 108, 120, rgb565(0, 255, 0))
    display.rect(52, 108, 72, 64, rgb565(0, 0, 255))
    display.fill_rect(144, 108, 72, 64, rgb565(0, 255, 255))
    display.text("pixel line rect fill", 28, 204, COLOR_TEXT, COLOR_BACKGROUND)
    display.pixel(0, 0, COLOR_TEXT)
    display.pixel(239, 0, COLOR_TEXT)
    display.pixel(0, 319, COLOR_TEXT)
    display.pixel(239, 319, COLOR_TEXT)
    wait(4000)


def typography(display):
    print("LCD_DIAGNOSTIC typography")
    display.begin_screen("Typography", "Status")
    display.draw_text_block(
        "Body text wraps by measured pixel width. Punctuation: !?.,:; Explicit newline follows.\nSecond line and Supercalifragilisticexpialidocious.",
        SCREEN_MARGIN,
        CONTENT_TOP + 12,
        SCREEN_WIDTH - SCREEN_MARGIN * 2,
        bottom=CONTENT_BOTTOM,
    )
    display.text("RIGHT", 200, CONTENT_BOTTOM - 16, COLOR_TEXT, COLOR_BACKGROUND)
    wait(6000)


def run():
    print("LCD_DIAGNOSTIC_START")
    try:
        display = Display()
        display.power_on()
        basic_initialisation(display)
        primary_colours(display)
        orientation_and_offsets(display)
        primitives(display)
        typography(display)
        gc.collect()
        print("LCD_DIAGNOSTIC_COMPLETE free_heap=" + str(gc.mem_free()))
    except Exception as error:
        print("LCD_DIAGNOSTIC_ERROR " + type(error).__name__ + ": " + str(error))
        raise


if __name__ == "__main__":
    run()
