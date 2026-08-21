import gc
import time

from assets.registry import ASSETS, PLACEMENTS, REGIONS
from config.ui_config import (
    COLOR_BACKGROUND, COLOR_BORDER, COLOR_ERROR, COLOR_PRIMARY,
    COLOR_SELECTED_BG, COLOR_SELECTED_TEXT, COLOR_SUCCESS, COLOR_SURFACE,
    COLOR_TEXT, COLOR_TEXT_MUTED, CONTENT_BOTTOM, CONTENT_TOP,
    MENU_ROW_HEIGHT, SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X,
    STATE_ART_Y, STATE_TEXT_Y,
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
        ("Message", "Latest message preview", "menu_messages", "menu_messages_selected"),
        ("Presets", "Open saved presets", "menu_presets", "menu_presets_selected"),
        ("Settings", "Device and network", "menu_settings", "menu_settings_selected"),
    )
    for index, row in enumerate(rows):
        label, subtitle, icon, selected_icon = row
        display.draw_menu_row(index, label, index == 0, subtitle, icon, selected_icon)
    display.draw_nav_bar(left="Rotate", right="Open", left_icon="action_scroll", right_icon="nav_enter_select")


def messages(display):
    display.begin_screen("Messages", "Demo")
    display.draw_text_block(
        "Meet at the station at 18:30. This is mock gallery data only.",
        SCREEN_MARGIN, CONTENT_TOP + 20, SCREEN_WIDTH - SCREEN_MARGIN * 2,
    )
    display.draw_nav_bar(left="Back", right="Info", left_icon="nav_back", right_icon="action_info")


def loading_messages(display):
    display.draw_loading("Loading messages", "state_loading_message")


def presets(display):
    display.begin_screen("Preset 2 of 4", "Rotate")
    display.draw_text_block("On my way - see you soon.", SCREEN_MARGIN, CONTENT_TOP + 20, SCREEN_WIDTH - SCREEN_MARGIN * 2)
    display.draw_nav_bar(left="Rotate", right="Choose", left_icon="action_scroll", right_icon="nav_enter_select")


def loading_presets(display):
    display.draw_loading("Loading presets", "state_loading_presets")


def preset_actions(display):
    display.begin_screen("Send preset")
    display.draw_text_block("On my way - see you soon.", SCREEN_MARGIN, CONTENT_TOP + 20, SCREEN_WIDTH - SCREEN_MARGIN * 2)
    display.draw_nav_bar(left="Back", right="Send", selected=2, left_icon="nav_back", right_icon="nav_send")


def sending(display):
    display.draw_loading("Sending preset", "state_sending")


def success(display):
    display.show_error("state_success", "Success", "Preset sent successfully.")


def settings(display):
    display.begin_screen("Settings", "Rotate")
    rows = (
        ("Account", "menu_account"),
        ("Device", "menu_device"),
        ("Wi-Fi", "menu_wifi"),
        ("Graphics", "menu_graphics"),
    )
    for index, row in enumerate(rows):
        display.draw_menu_row(index, row[0], index == 2, icon=row[1])
    display.draw_nav_bar(left="Back", right="Edit", left_icon="nav_back", right_icon="nav_change_edit")


def wifi_status(display):
    display.begin_screen("Wi-Fi", "Online", "status_wifi_4")
    display.draw_asset("state_wifi_success", STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Network: MessageBox-Demo", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_SUCCESS)
    display.draw_nav_bar(left="Back", right="Change", left_icon="nav_back", right_icon="nav_change_edit")


def wifi_list(display):
    display.begin_screen("Wi-Fi networks", "Rotate", "status_wifi_4")
    rows = (
        ("MessageBox", -42, 3),
        ("Workshop", -58, 3),
        ("Guest", -67, 0),
        ("Studio", -74, 3),
        ("<hidden>", -88, 3),
    )
    for index, row in enumerate(rows):
        display.draw_wifi_row(index, row[0], row[1], row[2], index == 0)
    display.draw_nav_bar(left="Back", right="Enter", left_icon="nav_back", right_icon="nav_enter_select")


def connecting(display):
    display.begin_screen("Connecting", "Wi-Fi", "status_sync")
    display.draw_text_block("MessageBox-Demo\nConnecting with mock credentials", SCREEN_MARGIN, 96, SCREEN_WIDTH - SCREEN_MARGIN * 2)
    display.draw_nav_bar(center="Waiting", center_icon="action_disconnected")


def wifi_success(display):
    display.begin_screen("Connected", "Wi-Fi", "status_wifi_4")
    display.draw_asset("state_wifi_success", STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Network settings saved.", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_SUCCESS)
    display.draw_nav_bar(center="Connected", center_icon="action_connected")


def wifi_error(display):
    display.begin_screen("Connection failed", "Error", "status_wifi_error")
    display.draw_asset("state_wifi_error", STATE_ART_X, STATE_ART_Y)
    display.draw_text_block("Could not connect to the selected network.", SCREEN_MARGIN, STATE_TEXT_Y, SCREEN_WIDTH - SCREEN_MARGIN * 2, color=COLOR_ERROR)
    display.draw_nav_bar(left="Back", right="Scan", left_icon="nav_back", right_icon="action_refresh_scan")


def keyboard(display):
    display.begin_screen("Keyboard", "Rotate")
    display.text("Wi-Fi password", SCREEN_MARGIN, CONTENT_TOP + 8, COLOR_TEXT_MUTED, COLOR_BACKGROUND)
    display.fill_rect(12, 84, 216, 76, COLOR_SURFACE)
    display.rect(12, 84, 216, 76, COLOR_BORDER)
    display.text("messagebox", 16, 88, COLOR_TEXT, COLOR_SURFACE)
    display.text("< Backspace    _ Space", SCREEN_MARGIN, 176, COLOR_TEXT_MUTED, COLOR_BACKGROUND)
    display.text("Double press changes case", SCREEN_MARGIN, 200, COLOR_TEXT_MUTED, COLOR_BACKGROUND)
    keys = ("x", "y", "z", "1", "2")
    for index, key in enumerate(keys):
        x = 12 + index * 44
        background = COLOR_SELECTED_BG if index == 2 else COLOR_SURFACE
        foreground = COLOR_SELECTED_TEXT if index == 2 else COLOR_TEXT
        display.fill_rect(x, 236, 40, 40, background)
        display.rect(x, 236, 40, 40, COLOR_PRIMARY if index == 2 else COLOR_BORDER)
        display.text(key, x + 16, 248, foreground, background)
    display.draw_nav_bar(left="Rotate", center="Case", right="Press", left_icon="action_scroll", center_icon="nav_change_edit", right_icon="nav_enter_select")


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
        ("HTTP error", lambda item: error_screen(item, "state_http_error", "HTTP error", "The server returned an unexpected response.")),
        ("device error", lambda item: error_screen(item, "state_device_error", "Device error", "Storage could not be read. Press to continue.")),
        ("software error", lambda item: error_screen(item, "state_software_error", "Software error", "The response could not be parsed safely.")),
        ("generic error", lambda item: error_screen(item, "state_generic_error", "Unknown error", "Something unexpected happened. Press to continue.")),
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
