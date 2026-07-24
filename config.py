from micropython import const
from libraries.utils.ascii import (PIGEON, CAT, ANT_MAN, HTTP_ERROR_RUNS, DEVICE_ERROR_RUNS,
                                   SOFTWARE_ERROR_RUNS, WIFI_ERROR_RUNS, MESSAGES_NAV_UNSELECTED, MESSAGES_NAV_SELECTED,
                                   PRESETS_NAV_UNSELECTED, PRESETS_NAV_SELECTED, FULL_APP_BORDER_RUNS,
                                   SETTINGS_NAV_SELECTED, SETTINGS_NAV_UNSELECTED
                                   )
from config.keymap_layout import *

PIGEON_SCREEN = PIGEON
CAT_SCREEN = CAT
ANT_MAN_SCREEN = ANT_MAN
HTTP_ERROR_SCREEN = HTTP_ERROR_RUNS
DEVICE_ERROR_SCREEN = DEVICE_ERROR_RUNS
SOFTWARE_ERROR_SCREEN = SOFTWARE_ERROR_RUNS
WIFI_ERROR_SCREEN = WIFI_ERROR_RUNS
KEYBOARD_SCREEN = KEYBOARD_UI_RUNS
KEY_POS = CAROUSEL_GLYPH_POSITIONS
ALPHABET_ = ALPHABET


SERVER_URL = None
TOKEN = None

SEND_JACK_URL = "http://projectserver.org/send/jack"
SEND_ELLA_URL = "http://projectserver.org/send/ella"
READ_JACK_URL = "http://projectserver.org/read/jack"
READ_ELLA_URL = "http://projectserver.org/read/ella"
PRESETS_JACK_URL = "http://projectserver.org/presets/jack"
PRESETS_ELLA_URL = "http://projectserver.org/presets/ella"


WIFI_SSID: str = "VM6227403"
WIFI_PASSWORD: str = "9UdkuxiSxweybmpu"

PRESET_FILE: str = "./database/preset.txt"
NO_PRESETS_RESP: str = "No presets Upload on site"
IF_MESSAGE_NONE_DISP: str = "No new or saved messages!"

# I2C PINS
I2C_SCL_PIN: int = const(22)
I2C_SDA_PIN: int = const(21)
I2C_HEX_1: int = const(0x3C)
I2C_HEX_2: int = const(0x3D)

# OLED details
OLED_WIDTH: int = const(128)
OLED_HEIGHT: int = const(64)
OLED_TEXT_HEIGHT: int = const(8)
OLED_CHARS_PER_LINE: int = const(16)
OLED_MAX_LINES: int = const(6)
OLED_BORDER_WIDTH: int = const(127)
OLED_BORDER_HEIGHT: int = const(63)

OLED_BORDER_SCREEN = FULL_APP_BORDER_RUNS

# INPUT DEVICES
LEFT_DIAL = const(-1)
RIGHT_DIAL = const(1)
DIAL_EVENT = const(4)
BUTTON_PRESS = const(3)

MENU_Y_AXIS: int = const(54)
MENU_LINES_LENGTH: int = const(4)

CHECK_MESSAGES_EVERY_MS: int = const(1500)
CHECK_PRESETS_EVERY_MS: int = const(15000)


MENU_OPTIONS_SELECTED = (MESSAGES_NAV_SELECTED, PRESETS_NAV_SELECTED, SETTINGS_NAV_SELECTED)
MENU_OPTIONS_UNSELECTED = (MESSAGES_NAV_UNSELECTED, PRESETS_NAV_UNSELECTED, SETTINGS_NAV_UNSELECTED)
MENU_OPTION = const(0)
PRESETS_OPTION = const(1)
SETTINGS_OPTION = const(2)



MENU_BACK_BUTTON: str = "Back"
PRESET_SEND_BUTTON: str = "Send"



LOOP_SLEEP_MS: int = const(20)
INPUT_DEBOUNCE_MS: int = const(150)

DISPLAY_FILE: str = const("./database/display.txt")

# BOOTING

ERROR_CODES = {
    "0": "unknown",
    "10": "HTTP",
    "11": "HTTP POST",
    "12": "HTTP GET",
    "13": "HTTP Json Invalid",
    "20": "DEVICE ERR",
    "21": "Display Error",
    "22": "Read Storage Error",
    "23": "Write Storage Error",
    "24": "Input Error",
    "30": "Software Error",
    "31": "Math Error",
    "32": "Parsing Error",
    "40": "No WIFI",
}
