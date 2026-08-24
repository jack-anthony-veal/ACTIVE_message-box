from micropython import const

from libraries.config import Config


# API / NETWORK
TOKEN = cwvd7CsVgyy6xxbxupgw

SEND_JACK_URL = "http://projectserver.org/send/jack"
READ_ELLA_URL = "http://projectserver.org/read/ella"
PRESETS_JACK_URL = "http://projectserver.org/presets/jack"

NETWORK_CONFIG_FILE = "./config/network.ini"
API_GET_TIMEOUT_S = const(5)
API_POST_TIMEOUT_S = const(30)
HTTP_SUCCESS_MIN = const(200)
HTTP_SUCCESS_MAX_EXCLUSIVE = const(300)
HTTP_SEND_SUCCESS_STATUS = const(200)

WIFI_INTERFACE_RESET_DELAY_MS = const(20)
WIFI_CONNECT_POLL_INTERVAL_MS = const(1000)
WIFI_CONNECT_TIMEOUT_S = const(5)
WIFI_BOOT_CONNECT_TIMEOUT_S = const(10)
WIFI_NEW_NETWORK_TIMEOUT_S = const(10)
WIFI_FAILURE_DISPLAY_MS = const(3000)
WIFI_RESULT_DISPLAY_MS = const(5000)

try:
    _network_config = Config.read(NETWORK_CONFIG_FILE)
    WIFI_SSID = str(_network_config["login"]["ssid"])
    WIFI_PASSWORD = str(_network_config["login"]["pass"])
except (OSError, KeyError, TypeError):
    WIFI_SSID = ""
    WIFI_PASSWORD = ""


# STORAGE PATHS
DISPLAY_FILE = "./database/display.txt"
PRESET_FILE = "./database/preset.txt"
MESSAGE_STORAGE_KEY = "message"
PRESETS_STORAGE_KEY = "presets"
NO_PRESETS_RESP = "No presets Upload on site"
IF_MESSAGE_NONE_DISP = "No new or saved messages!"


# GPIO
DISPLAY_SCK_PIN = const(18)
DISPLAY_MOSI_PIN = const(23)
DISPLAY_DC_PIN = const(16)
DISPLAY_RESET_PIN = const(4)
DISPLAY_CS_PIN = const(5)

DIAL_CLK_PIN = const(26)
DIAL_DT_PIN = const(27)
BUTTON_PIN = const(25)
WAKE_PIN = const(33)


# DISPLAY HARDWARE
DISPLAY_SPI_BUS = const(2)
DISPLAY_SPI_BAUDRATE = const(20_000_000)
DISPLAY_SPI_POLARITY = const(0)
DISPLAY_SPI_PHASE = const(0)
DISPLAY_USE_CS = True
DISPLAY_ROTATION = const(0)
DISPLAY_COLOR_ORDER = const(0)
DISPLAY_INVERSION = True
DISPLAY_BUFFER_SIZE = const(0)
RGB565_BYTES_PER_PIXEL = const(2)


# DISPLAY GEOMETRY
SCREEN_WIDTH = const(240)
SCREEN_HEIGHT = const(320)
SCREEN_MARGIN = const(12)

STATUS_HEIGHT = const(24)
TITLE_HEIGHT = const(32)
NAV_HEIGHT = const(40)
CONTENT_TOP = const(STATUS_HEIGHT + TITLE_HEIGHT)
CONTENT_BOTTOM = const(SCREEN_HEIGHT - NAV_HEIGHT)
CONTENT_HEIGHT = const(CONTENT_BOTTOM - CONTENT_TOP)

SPACE_XS = const(4)
SPACE_SM = const(8)
SPACE_MD = const(16)
SPACE_LG = const(24)

STATE_ART_X = const(88)
STATE_ART_Y = const(96)
STATE_TEXT_Y = const(176)
STATE_TEXT_FALLBACK_OFFSET_Y = const(32)

ICON_SMALL = const(16)
ICON_MEDIUM = const(24)
ICON_LARGE = const(32)


# TYPOGRAPHY
FONT_WIDTH = const(8)
FONT_HEIGHT = const(16)
LINE_GAP = const(4)
LINE_HEIGHT = const(FONT_HEIGHT + LINE_GAP)
ASCII_PRINTABLE_START = const(0x20)
ASCII_PRINTABLE_END_EXCLUSIVE = const(0x7F)


# COLOURS
def rgb565(red, green, blue):
    return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


COLOR_BACKGROUND = const(0x0000)
COLOR_SURFACE = const(0x0000)
COLOR_SURFACE_ALT = const(0x0000)
COLOR_TEXT = const(0xEFBF)
COLOR_TEXT_MUTED = const(0x9517)
COLOR_PRIMARY = const(0x34DB)
COLOR_SUCCESS = const(0x2E6E)
COLOR_WARNING = const(0xF621)
COLOR_ERROR = const(0xE267)
COLOR_BORDER = const(0x42CE)
COLOR_SELECTED_BG = const(0x1B96)
COLOR_SELECTED_TEXT = const(0xFFFF)


# STATUS BAR
STATUS_TEXT_Y = const(4)
STATUS_ICON_Y = const(4)
STATUS_ICON_SLOTS = (216, 196, 176)
STATUS_ITEM_GAP = const(8)


# MENUS / LISTS
MENU_X = const(12)
MENU_WIDTH = const(216)
MENU_TOP = const(68)
MENU_ROW_HEIGHT = const(44)
MENU_ROW_GAP = const(4)
MENU_VISIBLE_ROWS = const(4)
MENU_SELECTED_STRIPE_WIDTH = const(4)
MENU_ICON_INSET_X = const(8)
MENU_TEXT_INSET_X = const(10)
MENU_TEXT_GAP = const(8)
MENU_TEXT_RIGHT_PADDING = const(10)
MENU_LABEL_Y_OFFSET = const(12)
MENU_LABEL_WITH_SUBTITLE_Y_OFFSET = const(1)
MENU_SUBTITLE_Y_OFFSET = const(21)

NAV_ICON_Y = const(288)
NAV_ICON_SLOTS = {
    1: (108,),
    2: (48, 168),
    3: (28, 108, 188),
    4: (18, 78, 138, 198),
    5: (12, 60, 108, 156, 204),
}
NAV_LEFT_INDEX = const(0)
NAV_CENTER_INDEX = const(1)
NAV_RIGHT_INDEX = const(2)
NAV_LOGICAL_COUNT = const(3)
NAV_MAX_ACTIONS = const(5)
NAV_SELECTED_X_PADDING = const(8)
NAV_SELECTED_Y_OFFSET = const(1)
NAV_SELECTED_WIDTH = const(40)
NAV_LABEL_Y_OFFSET = const(12)
TITLE_TEXT_Y_OFFSET = const(8)


# WIFI UI
WIFI_ROW_HEIGHT = const(40)
WIFI_LIST_X = const(8)
WIFI_LIST_WIDTH = const(224)
WIFI_NAME_X = const(16)
WIFI_LOCK_X = const(152)
WIFI_ICON_X = const(176)
WIFI_SIGNAL_X = const(196)
WIFI_VISIBLE_ROWS = const(5)
WIFI_SCAN_SSID_INDEX = const(0)
WIFI_SCAN_RSSI_INDEX = const(3)
WIFI_SCAN_SECURITY_INDEX = const(4)
WIFI_ROW_BORDER_TRIM = const(2)
WIFI_ROW_SELECTED_STRIPE_WIDTH = const(4)
WIFI_ROW_ICON_Y_OFFSET = const(12)
WIFI_ROW_LABEL_Y_OFFSET = const(4)
WIFI_ROW_SUBTITLE_Y_OFFSET = const(21)
WIFI_ROW_TEXT_GAP = const(8)
WIFI_RSSI_UNKNOWN = const(-100)
WIFI_RSSI_ONE_BAR = const(-80)
WIFI_RSSI_TWO_BARS = const(-67)
WIFI_RSSI_THREE_BARS = const(-60)
WIFI_RSSI_FOUR_BARS = const(-55)


# KEYBOARD UI
KEYBOARD_KEY_X = (12, 56, 100, 144, 188)
KEYBOARD_SELECTED_KEY_INDEX = const(2)
KEYBOARD_VISIBLE_KEYS = const(5)
KEYBOARD_KEY_Y = const(236)
KEYBOARD_KEY_WIDTH = const(40)
KEYBOARD_KEY_HEIGHT = const(40)
KEYBOARD_KEY_TEXT_Y_OFFSET = const(12)
KEYBOARD_TEXT_X = const(16)
KEYBOARD_TEXT_Y = const(88)
KEYBOARD_TEXT_COLUMNS = const(26)
KEYBOARD_TEXT_ROWS = const(2)
KEYBOARD_TEXT_LINE_HEIGHT = const(20)
KEYBOARD_TEXT_BOX_INSET = const(4)
KEYBOARD_TEXT_BOX_HEIGHT = const(76)
KEYBOARD_BACKSPACE_HELP_Y = const(176)
KEYBOARD_CASE_HELP_Y = const(200)
KEYBOARD_ENTER_HELP_Y = const(220)
KEYBOARD_ENTER_CHARACTER = const(126)
KEYBOARD_BACKSPACE_CHARACTER = const(60)


# INPUT
LEFT_DIAL = const(-1)
RIGHT_DIAL = const(1)
DIAL_EVENT = const(4)
BUTTON_PRESS = const(3)
BUTTON_DEBOUNCE_MS = const(150)

ENCODER_MIN_VALUE = const(0)
ENCODER_MAX_VALUE = const(1000)
ENCODER_RANGE_SIZE = const(ENCODER_MAX_VALUE - ENCODER_MIN_VALUE + 1)
ENCODER_WRAP_THRESHOLD = const(ENCODER_RANGE_SIZE // 2)
ENCODER_EVENT_DEBOUNCE_MS = const(275)
ENCODER_MIN_STEP_DELTA = const(2)
ENCODER_MAX_STEP_DELTA = const(100)
ENCODER_INCREMENT = const(1)


# TIMING
MILLISECONDS_PER_SECOND = const(1000)
MAIN_LOOP_UPDATE_DELAY_MS = const(2)
MAIN_LOOP_DRAW_DELAY_MS = const(2)
KEYBOARD_FRAME_INTERVAL_MS = const(25)
KEYBOARD_DOUBLE_PRESS_MS = const(400)
FATAL_ERROR_DISPLAY_MS = const(5000)
STARTUP_HTTP_TIMEOUT_S = const(5)
STARTUP_MIN_FREE_STORAGE_BYTES = const(16_384)


# BUFFER LIMITS
KEYBOARD_TEXT_LIMIT = const(28)


# STATE / MENU INDEXES
HOME_MESSAGE_INDEX = const(0)
HOME_PRESETS_INDEX = const(1)
HOME_SETTINGS_INDEX = const(2)
APP_FLAG_NON_FATAL_API = const(1 << 1)
APP_FLAG_NON_FATAL_STORAGE = const(1 << 4)

ERROR_UNKNOWN = const(0)
ERROR_HTTP_MIN = const(10)
ERROR_HTTP_MAX_EXCLUSIVE = const(14)
ERROR_HTTP_POST = const(11)
ERROR_HTTP_GET = const(12)
ERROR_DEVICE_MIN = const(20)
ERROR_DEVICE_MAX_EXCLUSIVE = const(25)
ERROR_STORAGE_READ = const(22)
ERROR_SOFTWARE_MIN = const(30)
ERROR_SOFTWARE_MAX_EXCLUSIVE = const(33)
ERROR_WIFI = const(40)


# ERROR CODES
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


def menu_row_y(row_index):
    return MENU_TOP + row_index * (MENU_ROW_HEIGHT + MENU_ROW_GAP)


def visible_window(total, selected, limit=MENU_VISIBLE_ROWS):
    if total <= 0:
        return 0, 0
    if selected < 0:
        selected = 0
    if selected >= total:
        selected = total - 1
    if total <= limit:
        return 0, total
    start = selected - (limit // 2)
    if start < 0:
        start = 0
    maximum_start = total - limit
    if start > maximum_start:
        start = maximum_start
    return start, start + limit
