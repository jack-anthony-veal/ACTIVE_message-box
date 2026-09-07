import gc
import time

from assets.registry import ASSETS, ICONS, PLACEMENTS, REGIONS
from config.config import (
    COLOR_BACKGROUND, COLOR_BORDER, COLOR_ERROR, COLOR_PRIMARY,
    COLOR_SELECTED_BG, COLOR_SELECTED_TEXT, COLOR_SUCCESS, COLOR_SURFACE,
    COLOR_TEXT, COLOR_TEXT_MUTED, CONTENT_BOTTOM, CONTENT_TOP,
    KEYBOARD_BACKSPACE_HELP_Y, KEYBOARD_CASE_HELP_Y, KEYBOARD_KEY_HEIGHT,
    KEYBOARD_KEY_TEXT_Y_OFFSET, KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_X,
    KEYBOARD_KEY_Y, KEYBOARD_SELECTED_KEY_INDEX, KEYBOARD_TEXT_BOX_HEIGHT,
    KEYBOARD_TEXT_BOX_INSET, KEYBOARD_TEXT_X, KEYBOARD_TEXT_Y, SCREEN_MARGIN,
    SCREEN_WIDTH, SPACE_SM, STATE_ART_X, STATE_ART_Y, STATE_TEXT_Y,
    LINE_HEIGHT, NAV_RIGHT_INDEX,
)
from hardware_devices.display_device import Display


def validate_layouts():
    for screen, name, x, y, region_name in PLACEMENTS:
        _, width, height = ASSETS[name]
        region_x, region_y, region_width, region_height = REGIONS[region_name]
        valid = (
            x >= region_x and y >= region_y
            and x + width <= region_x + region_width
            and y + height <= region_y + region_height
        )
        if not valid:
            raise ValueError("invalid layout {} {}".format(screen, name))


def home(display):
    display.begin_screen("Home", "Rotate")
    rows = (
        ("Message", "Latest message preview", ICONS["menu"]["messages"], ICONS["menu"]["messages_selected"]),
        ("Presets", "Open saved presets", ICONS["menu"]["presets"], ICONS["menu"]["presets_selected"]),
        ("Settings", "Device and network", ICONS["menu"]["settings"], ICONS["menu"]["settings_selected"]),
    )
    for index, row in enumerate(rows):
        label, subtitle, icon, selected_icon = row
        display.draw_menu_row(index, label, index == 0, subtitle, icon, selected_icon)
    display.draw_nav_bar(left="Rotate", right="Open", left_icon=ICONS["action"]["scroll"], right_icon=ICONS["navigation"]["select"])


def messages(display):
    display.begin_screen("Messages", "Demo")
    display.draw_text_block(
        "Meet at the station at 18:30. This is mock gallery data only.",
        SCREEN_MARGIN, CONTENT_TOP + LINE_HEIGHT,
        SCREEN_WIDTH - SCREEN_MARGIN * 2,
    )
    display.draw_nav_bar(left="Back", right="Info", left_icon=ICONS["navigation"]["back"], right_icon=ICONS["action"]["info"])


def loading_messages(display):
    display.draw_loading("Loading messages", ICONS["state"]["loading_message"])


def presets(display):
    display.begin_screen("Preset 2 of 4", "Rotate")
    display.draw_text_block(
        "On my way - see you soon.", SCREEN_MARGIN,
        CONTENT_TOP + LINE_HEIGHT, SCREEN_WIDTH - SCREEN_MARGIN * 2,
    )
    display.draw_nav_bar(left="Rotate", right="Choose", left_icon=ICONS["action"]["scroll"], right_icon=ICONS["navigation"]["select"])


def loading_presets(display):
    display.draw_loading("Loading presets", ICONS["state"]["loading_presets"])


def preset_actions(display):
    display.begin_screen("Send preset")
    display.draw_text_block(
        "On my way - see you soon.", SCREEN_MARGIN,
        CONTENT_TOP + LINE_HEIGHT, SCREEN_WIDTH - SCREEN_MARGIN * 2,
    )
    display.draw_nav_bar(
        left="Back", right="Send", selected=NAV_RIGHT_INDEX,
        left_icon=ICONS["navigation"]["back"],
        right_icon=ICONS["navigation"]["send"],
    )


def sending(display):
    display.draw_loading("Sending preset", ICONS["state"]["sending"])


def success(display):
    display.show_error(ICONS["state"]["success"], "Success", "Preset sent successfully.")


def settings(display):
    display.begin_screen("Settings", "Rotate")
    rows = (
        ("Account", ICONS["menu"]["account"]),
        ("Device", ICONS["menu"]["device"]),
        ("Wi-Fi", ICONS["menu"]["wifi"]),
        ("Graphics", ICONS["menu"]["graphics"]),
    )
    for index, row in enumerate(rows):
        display.draw_menu_row(index, row[0], index == 2, icon=row[1])
    display.draw_nav_bar(left="Back", right="Edit", left_icon=ICONS["navigation"]["back"], right_icon=ICONS["navigation"]["edit"])


def wifi_status(display):
    display.begin_screen("Wi-Fi", "Online", ICONS["status"]["wifi_4"])
    display.draw_asset(ICONS["state"]["wifi_success"], STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Network: MessageBox-Demo", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_SUCCESS)
    display.draw_nav_bar(left="Back", right="Change", left_icon=ICONS["navigation"]["back"], right_icon=ICONS["navigation"]["edit"])


def wifi_list(display):
    display.begin_screen("Wi-Fi networks", "Rotate", ICONS["status"]["wifi_4"])
    rows = (
        ("MessageBox", -42, 3),
        ("Workshop", -58, 3),
        ("Guest", -67, 0),
        ("Studio", -74, 3),
        ("<hidden>", -88, 3),
    )
    signal_icons = (
        ICONS["status"]["wifi_4"], ICONS["status"]["wifi_3"],
        ICONS["status"]["wifi_2"], ICONS["status"]["wifi_1"],
        ICONS["status"]["wifi_0"],
    )
    for index, row in enumerate(rows):
        display.draw_list_row(
            index, row[0], str(row[1]) + " dBm", index == 0,
            signal_icons[index],
            ICONS["status"]["lock"] if row[2] else None,
        )
    display.draw_nav_bar(left="Back", right="Enter", left_icon=ICONS["navigation"]["back"], right_icon=ICONS["navigation"]["select"])


def connecting(display):
    display.begin_screen("Connecting", "Wi-Fi", ICONS["status"]["sync"])
    display.draw_text_block(
        "MessageBox-Demo\nConnecting with mock credentials",
        SCREEN_MARGIN, STATE_ART_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2,
    )
    display.draw_nav_bar(center="Waiting", center_icon=ICONS["action"]["disconnected"])


def wifi_success(display):
    display.begin_screen("Connected", "Wi-Fi", ICONS["status"]["wifi_4"])
    display.draw_asset(ICONS["state"]["wifi_success"], STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Network settings saved.", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_SUCCESS)
    display.draw_nav_bar(center="Connected", center_icon=ICONS["action"]["connected"])


def wifi_error(display):
    display.begin_screen("Connection failed", "Error", ICONS["status"]["wifi_error"])
    display.draw_asset(ICONS["state"]["wifi_error"], STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Could not connect to the selected network.", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_ERROR)
    display.draw_nav_bar(left="Back", right="Scan", left_icon=ICONS["navigation"]["back"], right_icon=ICONS["action"]["refresh"])


def keyboard(display):
    display.begin_screen("Keyboard", "Rotate")
    display.text(
        "Wi-Fi password", SCREEN_MARGIN, CONTENT_TOP + SPACE_SM,
        COLOR_TEXT_MUTED, COLOR_BACKGROUND,
    )
    box_x = KEYBOARD_TEXT_X - KEYBOARD_TEXT_BOX_INSET
    box_y = KEYBOARD_TEXT_Y - KEYBOARD_TEXT_BOX_INSET
    box_width = SCREEN_WIDTH - box_x * 2
    display.fill_rect(
        box_x, box_y, box_width, KEYBOARD_TEXT_BOX_HEIGHT, COLOR_SURFACE
    )
    display.rect(
        box_x, box_y, box_width, KEYBOARD_TEXT_BOX_HEIGHT, COLOR_BORDER
    )
    display.text(
        "messagebox", KEYBOARD_TEXT_X, KEYBOARD_TEXT_Y,
        COLOR_TEXT, COLOR_SURFACE,
    )
    display.text(
        "< Backspace    _ Space", SCREEN_MARGIN, KEYBOARD_BACKSPACE_HELP_Y,
        COLOR_TEXT_MUTED, COLOR_BACKGROUND,
    )
    display.text(
        "Double press changes case", SCREEN_MARGIN, KEYBOARD_CASE_HELP_Y,
        COLOR_TEXT_MUTED, COLOR_BACKGROUND,
    )
    keys = ("x", "y", "z", "1", "2")
    for index, key in enumerate(keys):
        x = KEYBOARD_KEY_X[index]
        selected = index == KEYBOARD_SELECTED_KEY_INDEX
        background = COLOR_SELECTED_BG if selected else COLOR_SURFACE
        foreground = COLOR_SELECTED_TEXT if selected else COLOR_TEXT
        display.fill_rect(
            x, KEYBOARD_KEY_Y,
            KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_HEIGHT, background,
        )
        display.rect(
            x, KEYBOARD_KEY_Y,
            KEYBOARD_KEY_WIDTH, KEYBOARD_KEY_HEIGHT,
            COLOR_PRIMARY if selected else COLOR_BORDER,
        )
        display.text(
            key,
            x + (KEYBOARD_KEY_WIDTH - display.measure_text(key)) // 2,
            KEYBOARD_KEY_Y + KEYBOARD_KEY_TEXT_Y_OFFSET,
            foreground, background,
        )
    display.draw_nav_bar(
        left="Rotate", center="Case", right="Press",
        left_icon=ICONS["action"]["scroll"],
        center_icon=ICONS["navigation"]["edit"],
        right_icon=ICONS["navigation"]["select"],
    )


def error_screen(display, asset_name, title, body):
    display.show_error(asset_name, title, body)


def run(hold_ms=4000):
    validate_layouts()
    display = Display()
    display.power_on()
    screens = (
        ("main/home menu", home),
        ("messages", messages),
        ("loading messages", loading_messages),
        ("presets", presets),
        ("loading presets", loading_presets),
        ("preset actions", preset_actions),
        ("sending", sending),
        ("success/notification", success),
        ("settings", settings),
        ("Wi-Fi status", wifi_status),
        ("Wi-Fi network list", wifi_list),
        ("connecting", connecting),
        ("Wi-Fi success", wifi_success),
        ("Wi-Fi error", wifi_error),
        ("keyboard", keyboard),
        ("HTTP error", lambda item: error_screen(item, ICONS["state"]["http_error"], "HTTP error", "The server returned an unexpected response.")),
        ("device error", lambda item: error_screen(item, ICONS["state"]["device_error"], "Device error", "Storage could not be read. Press to continue.")),
        ("software error", lambda item: error_screen(item, ICONS["state"]["software_error"], "Software error", "The response could not be parsed safely.")),
        ("generic error", lambda item: error_screen(item, ICONS["state"]["generic_error"], "Unknown error", "Something unexpected happened. Press to continue.")),
    )
    print("SCREEN_GALLERY_START count=" + str(len(screens)))
    minimum_heap = gc.mem_free()
    for index, item in enumerate(screens):
        name, renderer = item
        gc.collect()
        before = gc.mem_free()
        print("SCREEN {}/{} {} before={}".format(index + 1, len(screens), name, before))
        renderer(display)
        gc.collect()
        after = gc.mem_free()
        if after < minimum_heap:
            minimum_heap = after
        print("SCREEN_DONE {} after={} delta={}".format(name, after, after - before))
        time.sleep_ms(hold_ms)
    display.fill(COLOR_BACKGROUND)
    gc.collect()
    print("SCREEN_GALLERY_COMPLETE free_heap={} minimum_heap={}".format(gc.mem_free(), minimum_heap))


if __name__ == "__main__":
    run()
