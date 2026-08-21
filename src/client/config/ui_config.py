from micropython import const


def rgb565(red, green, blue):
    return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


SCREEN_WIDTH = const(240)
SCREEN_HEIGHT = const(320)

SCREEN_MARGIN = const(12)

STATUS_HEIGHT = const(24)
TITLE_HEIGHT = const(32)
NAV_HEIGHT = const(40)

CONTENT_TOP = const(56)
CONTENT_BOTTOM = const(280)
CONTENT_HEIGHT = const(224)

SPACE_XS = const(4)
SPACE_SM = const(8)
SPACE_MD = const(16)
SPACE_LG = const(24)

MENU_X = const(12)
MENU_WIDTH = const(216)
MENU_TOP = const(68)
MENU_ROW_HEIGHT = const(44)
MENU_ROW_GAP = const(4)
MENU_VISIBLE_ROWS = const(4)

WIFI_ROW_HEIGHT = const(40)
WIFI_LIST_X = const(8)
WIFI_LIST_WIDTH = const(224)
WIFI_NAME_X = const(16)
WIFI_LOCK_X = const(152)
WIFI_ICON_X = const(176)
WIFI_SIGNAL_X = const(196)

STATUS_ICON_Y = const(4)
STATUS_ICON_SLOTS = (216, 196, 176)
NAV_ICON_Y = const(288)
NAV_ICON_SLOTS = {
    1: (108,),
    2: (48, 168),
    3: (28, 108, 188),
    4: (18, 78, 138, 198),
    5: (12, 60, 108, 156, 204),
}
STATE_ART_X = const(88)
STATE_ART_Y = const(96)
STATE_TEXT_Y = const(176)

ICON_SMALL = const(16)
ICON_MEDIUM = const(24)
ICON_LARGE = const(32)

FONT_WIDTH = const(8)
FONT_HEIGHT = const(16)
LINE_GAP = const(4)
LINE_HEIGHT = const(FONT_HEIGHT + LINE_GAP)

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
