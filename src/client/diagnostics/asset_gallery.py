import gc
import time

from assets.registry import ASSETS
from config.config import (
    COLOR_BACKGROUND, COLOR_TEXT, COLOR_TEXT_MUTED, CONTENT_BOTTOM,
    ICON_MEDIUM, ICON_SMALL, RGB565_BYTES_PER_PIXEL, SCREEN_MARGIN,
    SCREEN_WIDTH, STATE_ART_Y, STATE_TEXT_Y,
)
from hardware_devices.display_device import Display


def run(hold_ms=2000):
    print("ASSET_GALLERY_START count=" + str(len(ASSETS)))
    display = Display()
    display.power_on()
    names = sorted(ASSETS)
    minimum_heap = gc.mem_free()
    for index, name in enumerate(names):
        path, width, height = ASSETS[name]
        gc.collect()
        before = gc.mem_free()
        print("ASSET {}/{} {} {}x{} before={}".format(index + 1, len(names), name, width, height, before))
        display.begin_screen("Asset {}/{}".format(index + 1, len(names)))
        x = (SCREEN_WIDTH - width) // 2
        y = (
            STATE_ART_Y
            if height > ICON_MEDIUM
            else STATE_ART_Y + ICON_SMALL
        )
        display.draw_asset(name, x, y)
        display.draw_text_block(
            name, SCREEN_MARGIN, STATE_TEXT_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
            color=COLOR_TEXT,
            max_lines=2,
            bottom=CONTENT_BOTTOM,
        )
        display.text(
            "{}x{} {} bytes".format(
                width, height, width * height * RGB565_BYTES_PER_PIXEL
            ),
            SCREEN_MARGIN,
            CONTENT_BOTTOM - ICON_MEDIUM,
            COLOR_TEXT_MUTED,
            COLOR_BACKGROUND,
        )
        gc.collect()
        after = gc.mem_free()
        if after < minimum_heap:
            minimum_heap = after
        print("ASSET_DONE {} after={} delta={}".format(name, after, after - before))
        time.sleep_ms(hold_ms)
    display.fill(COLOR_BACKGROUND)
    gc.collect()
    print("ASSET_GALLERY_COMPLETE free_heap={} minimum_heap={}".format(gc.mem_free(), minimum_heap))


if __name__ == "__main__":
    run()
