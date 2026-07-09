from typing import *

SERVER_URL: str = "https://projectserver.org"
TOKEN: str = "cwvd7CsVgyy6xxbxupgw" # should change to be more secure

WIFI_SSID: str = "VM6227403"
WIFI_PASSWORD: str = "9UdkuxiSxweybmpu"

READ_PERSON: str = "ella"
PRESET_PERSON: str = "jack"
PRESET_FILE: str = "preset.txt"

OLED_WIDTH: int = 128
OLED_HEIGHT: int = 64
OLED_TEXT_HEIGHT: int = 8
OLED_CHARS_PER_LINE: int = 16
OLED_MAX_LINES: int = 6

I2C_SCL_PIN: int = 22
I2C_SDA_PIN: int = 21

LEFT_PIN: int = 25
RIGHT_PIN: int = 26
RIGHT_PIN_CHECK: int = 0
LEFT_PIN_CHECK: int = 1

MENU_Y: int = 54
MENU_LINES_LENGTH = 4


CHECK_MESSAGES_EVERY_MS: int = 10000
CHECK_PRESETS_EVERY_MS: int = 10000

MENU_OPTIONS: list = ["Messages", "Presets", "Settings"]
MENU_OPTS_INDEX: list[Tuple[int, str, Union[int, None]]] = [
    (0, MENU_OPTIONS[0], CHECK_MESSAGES_EVERY_MS ),
    (1, MENU_OPTIONS[1], CHECK_PRESETS_EVERY_MS ),
    (2, MENU_OPTIONS[2], None)
]

MENU_CYCLE_ICON = ' > '
MENU_BACK_BUTTON: str = "Back"
PRESET_SEND_BUTTON: str = "Send"



CHECK_MS_DICT = {"CHECK_MESSAGES_EVERY_MS": 10000,
"CHECK_PRESETS_EVERY_MS": 15000}
LOOP_SLEEP_MS: int = 20
INPUT_DEBOUNCE_MS: int = 150

DISPLAY_FILE: str = "display.txt"

# BOOTING
BOOT_MESSAGE: str = "Hi ella! Booting up now. Love you xx - Jack <3"
BOOT_DISPLAY_LAYOUT = {"status": 0, "result": 6}
JUST_BOOTED: bool = True
