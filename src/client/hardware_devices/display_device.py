import gc

from assets.registry import ASSETS, ICONS, asset
from config.config import (
    ASCII_PRINTABLE_END_EXCLUSIVE, ASCII_PRINTABLE_START, COLOR_BACKGROUND,
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SELECTED_BG, COLOR_SELECTED_TEXT,
    COLOR_SURFACE, COLOR_SURFACE_ALT, COLOR_TEXT, COLOR_TEXT_MUTED,
    CONTENT_BOTTOM, CONTENT_TOP, DISPLAY_COLOR_ORDER, DISPLAY_CS_PIN,
    DISPLAY_BUFFER_SIZE, DISPLAY_DC_PIN, DISPLAY_INVERSION, DISPLAY_MOSI_PIN,
    DISPLAY_RESET_PIN,
    DISPLAY_ROTATION, DISPLAY_SCK_PIN, DISPLAY_SPI_BAUDRATE, DISPLAY_SPI_BUS,
    DISPLAY_SPI_PHASE, DISPLAY_SPI_POLARITY, DISPLAY_USE_CS, FONT_HEIGHT,
    FONT_WIDTH, ICON_MEDIUM, ICON_SMALL, LINE_HEIGHT, MENU_ICON_INSET_X,
    MENU_LABEL_WITH_SUBTITLE_Y_OFFSET, MENU_LABEL_Y_OFFSET, MENU_ROW_HEIGHT,
    MENU_SELECTED_STRIPE_WIDTH, MENU_SUBTITLE_Y_OFFSET, MENU_TEXT_GAP,
    MENU_TEXT_INSET_X, MENU_TEXT_RIGHT_PADDING, MENU_WIDTH, MENU_X,
    NAV_HEIGHT, NAV_ICON_SLOTS, NAV_ICON_Y, NAV_LABEL_Y_OFFSET,
    NAV_LOGICAL_COUNT, NAV_MAX_ACTIONS, NAV_SELECTED_WIDTH,
    NAV_SELECTED_X_PADDING, NAV_SELECTED_Y_OFFSET, RGB565_BYTES_PER_PIXEL,
    SCREEN_HEIGHT, SCREEN_MARGIN, SCREEN_WIDTH, STATE_ART_X, STATE_ART_Y,
    STATE_TEXT_FALLBACK_OFFSET_Y, STATE_TEXT_Y, STATUS_HEIGHT,
    STATUS_ICON_SLOTS, STATUS_ICON_Y, STATUS_ITEM_GAP, STATUS_TEXT_Y,
    TITLE_HEIGHT, TITLE_TEXT_Y_OFFSET, WIFI_ICON_X, WIFI_LIST_WIDTH,
    WIFI_LIST_X, WIFI_LOCK_X, WIFI_NAME_X, WIFI_ROW_BORDER_TRIM,
    WIFI_ROW_HEIGHT, WIFI_ROW_ICON_Y_OFFSET, WIFI_ROW_LABEL_Y_OFFSET,
    WIFI_ROW_SELECTED_STRIPE_WIDTH, WIFI_ROW_SUBTITLE_Y_OFFSET,
    WIFI_ROW_TEXT_GAP, WIFI_SIGNAL_X, menu_row_y,
)
from fonts import vga1_8x16
from libraries.utils.text_layout import layout_text


class Display:
    def __init__(self, backend=None, asset_root=""):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.font = vga1_8x16
        self.font_width = FONT_WIDTH
        self.font_height = FONT_HEIGHT
        self.spi = None
        self.asset_root = str(asset_root).rstrip("/")

        if backend is None:
            from machine import Pin, SPI
            import st7789

            self.spi = SPI(
                DISPLAY_SPI_BUS,
                baudrate=DISPLAY_SPI_BAUDRATE,
                polarity=DISPLAY_SPI_POLARITY,
                phase=DISPLAY_SPI_PHASE,
                sck=Pin(DISPLAY_SCK_PIN),
                mosi=Pin(DISPLAY_MOSI_PIN),
            )
            keyword_args = {
                "reset": Pin(DISPLAY_RESET_PIN, Pin.OUT),
                "dc": Pin(DISPLAY_DC_PIN, Pin.OUT),
                "rotation": DISPLAY_ROTATION,
                "color_order": DISPLAY_COLOR_ORDER,
                "inversion": DISPLAY_INVERSION,
                "buffer_size": DISPLAY_BUFFER_SIZE,
            }
            if DISPLAY_USE_CS:
                keyword_args["cs"] = Pin(DISPLAY_CS_PIN, Pin.OUT)

            backend = st7789.ST7789(
                self.spi, SCREEN_WIDTH, SCREEN_HEIGHT, **keyword_args
            )
            backend.init()

        self._backend = backend

    def blit_buffer(self, data, x, y, width, height):
        x = int(x)
        y = int(y)
        width = int(width)
        height = int(height)
        expected = width * height * RGB565_BYTES_PER_PIXEL
        if width < 1 or height < 1:
            raise ValueError("bitmap dimensions must be positive")
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise ValueError("bitmap placement is outside the display")
        if len(data) != expected:
            raise ValueError("invalid bitmap size: expected {} bytes, got {}".format(expected, len(data)))
        self._backend.blit_buffer(data, x, y, width, height)

    def draw_asset(self, name, x, y):
        path, width, height = asset(name)
        path = str(path).replace("\\", "/")
        parts = path.split("/")
        if path.startswith("/") or ".." in parts or parts[:2] != ["assets", "bin"]:
            raise ValueError("asset path is outside assets/bin")
        if self.asset_root:
            path = self.asset_root + "/" + path
        expected = width * height * RGB565_BYTES_PER_PIXEL
        with open(path, "rb") as asset_file:
            data = asset_file.read(expected + 1)
        if len(data) != expected:
            actual = len(data)
            del data
            gc.collect()
            raise ValueError("invalid asset size for {}: expected {} bytes, got {}".format(name, expected, actual))
        try:
            self.blit_buffer(data, x, y, width, height)
        finally:
            del data
            gc.collect()
        return x, y, width, height

    def fill(self, color=COLOR_BACKGROUND):
        self._backend.fill(color)

    def pixel(self, x, y, color=COLOR_TEXT):
        self._backend.pixel(x, y, color)

    def line(self, x0, y0, x1, y1, color=COLOR_TEXT):
        self._backend.line(x0, y0, x1, y1, color)

    def hline(self, x, y, length, color=COLOR_TEXT):
        self._backend.hline(x, y, length, color)

    def vline(self, x, y, length, color=COLOR_TEXT):
        self._backend.vline(x, y, length, color)

    def rect(self, x, y, width, height, color=COLOR_BORDER):
        self._backend.rect(x, y, width, height, color)

    def fill_rect(self, x, y, width, height, color=COLOR_SURFACE):
        self._backend.fill_rect(x, y, width, height, color)

    @staticmethod
    def _font_safe(value):
        value = str(value)
        return "".join(
            character
            if ASCII_PRINTABLE_START <= ord(character) < ASCII_PRINTABLE_END_EXCLUSIVE
            else "?"
            for character in value
        )

    def text(self, value, x, y, color=COLOR_TEXT, background=COLOR_BACKGROUND, font=None):
        font = self.font if font is None else font
        safe_value = self._font_safe(value)
        self._backend.text(font, safe_value, int(x), int(y), color, background)

    def measure_text(self, value, font=None):
        font = self.font if font is None else font
        return len(self._font_safe(value)) * font.WIDTH

    def text_lines(self, value, max_width, max_lines=None):
        return layout_text(value, max_width, self.measure_text, max_lines)

    def draw_text_block(
        self, value, x, y, max_width, color=COLOR_TEXT,
        background=COLOR_BACKGROUND, line_height=LINE_HEIGHT,
        max_lines=None, bottom=CONTENT_BOTTOM,
    ):
        available_lines = 0
        if y < bottom:
            available_lines = ((bottom - y - self.font_height) // line_height) + 1
        if available_lines < 0:
            available_lines = 0
        if max_lines is None or max_lines > available_lines:
            max_lines = available_lines
        lines = self.text_lines(value, max_width, max_lines)
        for index, line_text in enumerate(lines):
            self.text(line_text, x, y + index * line_height, color, background)
        return y + len(lines) * line_height

    def power_on(self):
        try:
            if hasattr(self._backend, "sleep_mode"):
                self._backend.sleep_mode(False)
            if hasattr(self._backend, "on"):
                self._backend.on()
        except Exception:
            gc.collect()
            raise

    def power_off(self):
        if hasattr(self._backend, "off"):
            self._backend.off()
        if hasattr(self._backend, "sleep_mode"):
            self._backend.sleep_mode(True)

    def draw_status_bar(self, label="MESSAGE BOX", status="", status_asset=None):
        self.fill_rect(0, 0, SCREEN_WIDTH, STATUS_HEIGHT, COLOR_SURFACE_ALT)
        self.text(
            label, SCREEN_MARGIN, STATUS_TEXT_Y,
            COLOR_TEXT, COLOR_SURFACE_ALT,
        )
        status_right = SCREEN_WIDTH - SCREEN_MARGIN
        if status_asset:
            if isinstance(status_asset, str):
                status_assets = (status_asset,)
            else:
                status_assets = tuple(status_asset)
            if len(status_assets) > len(STATUS_ICON_SLOTS):
                raise ValueError("too many status assets")
            for index, icon_name in enumerate(status_assets):
                _, icon_width, icon_height = asset(icon_name)
                if icon_width != ICON_SMALL or icon_height != ICON_SMALL:
                    raise ValueError("status asset must be 16x16")
                self.draw_asset(icon_name, STATUS_ICON_SLOTS[index], STATUS_ICON_Y)
            status_right = STATUS_ICON_SLOTS[len(status_assets) - 1] - STATUS_ITEM_GAP
        if status:
            status = self._font_safe(status)
            status_left = SCREEN_MARGIN + self.measure_text(label) + STATUS_ITEM_GAP
            available = status_right - status_left
            if available > 0:
                status = status[:available // self.font_width]
                x = status_right - self.measure_text(status)
                self.text(
                    status, x, STATUS_TEXT_Y,
                    COLOR_TEXT_MUTED, COLOR_SURFACE_ALT,
                )

    def draw_title(self, title):
        y = STATUS_HEIGHT
        self.fill_rect(0, y, SCREEN_WIDTH, TITLE_HEIGHT, COLOR_SURFACE)
        title_lines = self.text_lines(title, SCREEN_WIDTH - SCREEN_MARGIN * 2, 1)
        title_text = title_lines[0] if title_lines else ""
        self.text(
            title_text, SCREEN_MARGIN, y + TITLE_TEXT_Y_OFFSET,
            COLOR_PRIMARY, COLOR_SURFACE,
        )
        self.hline(0, CONTENT_TOP - 1, SCREEN_WIDTH, COLOR_BORDER)

    def begin_screen(self, title, status="", status_asset=None):
        self.fill(COLOR_BACKGROUND)
        self.draw_status_bar(status=status, status_asset=status_asset)
        self.draw_title(title)

    def draw_menu_row(
        self, row, label, selected=False, subtitle=None,
        icon=None, selected_icon=None,
    ):
        y = menu_row_y(row)
        background = COLOR_SELECTED_BG if selected else COLOR_SURFACE
        foreground = COLOR_SELECTED_TEXT if selected else COLOR_TEXT
        self.fill_rect(MENU_X, y, MENU_WIDTH, MENU_ROW_HEIGHT, background)
        self.rect(
            MENU_X, y, MENU_WIDTH, MENU_ROW_HEIGHT,
            COLOR_PRIMARY if selected else COLOR_BORDER,
        )
        if selected:
            self.fill_rect(
                MENU_X, y, MENU_SELECTED_STRIPE_WIDTH,
                MENU_ROW_HEIGHT, COLOR_PRIMARY,
            )
        text_x = MENU_X + MENU_TEXT_INSET_X
        if icon:
            icon_name = icon
            if selected and selected_icon and selected_icon in ASSETS:
                icon_name = selected_icon
            _, icon_width, icon_height = asset(icon_name)
            icon_x = MENU_X + MENU_ICON_INSET_X
            icon_y = y + (MENU_ROW_HEIGHT - icon_height) // 2
            self.draw_asset(icon_name, icon_x, icon_y)
            text_x = icon_x + icon_width + MENU_TEXT_GAP
        label_y = y + (
            MENU_LABEL_Y_OFFSET
            if subtitle is None
            else MENU_LABEL_WITH_SUBTITLE_Y_OFFSET
        )
        self.text(label, text_x, label_y, foreground, background)
        if subtitle is not None:
            lines = self.text_lines(
                subtitle,
                MENU_X + MENU_WIDTH - MENU_TEXT_RIGHT_PADDING - text_x,
                1,
            )
            subtitle_text = lines[0] if lines else ""
            subtitle_color = COLOR_SELECTED_TEXT if selected else COLOR_TEXT_MUTED
            self.text(
                subtitle_text, text_x, y + MENU_SUBTITLE_Y_OFFSET,
                subtitle_color, background,
            )
        return y

    def draw_nav_bar(
        self, left="", center="", right="", selected=None,
        left_icon=None, center_icon=None, right_icon=None,
    ):
        y = SCREEN_HEIGHT - NAV_HEIGHT
        self.fill_rect(0, y, SCREEN_WIDTH, NAV_HEIGHT, COLOR_SURFACE_ALT)
        self.hline(0, y, SCREEN_WIDTH, COLOR_BORDER)
        labels = (left, center, right)
        icons = (left_icon, center_icon, right_icon)
        actions = []
        for logical_index in range(NAV_LOGICAL_COUNT):
            if labels[logical_index] or icons[logical_index]:
                actions.append((logical_index, labels[logical_index], icons[logical_index]))
        if len(actions) > NAV_MAX_ACTIONS:
            raise ValueError("too many navigation actions")
        slots = NAV_ICON_SLOTS.get(len(actions), ())
        for action_index, action in enumerate(actions):
            logical_index, label, icon_name = action
            x = slots[action_index]
            if selected == logical_index:
                self.fill_rect(
                    x - NAV_SELECTED_X_PADDING,
                    y + NAV_SELECTED_Y_OFFSET,
                    NAV_SELECTED_WIDTH,
                    NAV_HEIGHT - NAV_SELECTED_Y_OFFSET,
                    COLOR_SELECTED_BG,
                )
            if icon_name:
                _, icon_width, icon_height = asset(icon_name)
                if icon_width != ICON_MEDIUM or icon_height != ICON_MEDIUM:
                    raise ValueError("navigation asset must be 24x24")
                self.draw_asset(icon_name, x, NAV_ICON_Y)
            elif label:
                label_width = self.measure_text(label)
                self.text(
                    label,
                    x + (ICON_MEDIUM - label_width) // 2,
                    y + NAV_LABEL_Y_OFFSET,
                    COLOR_SELECTED_TEXT if selected == logical_index else COLOR_TEXT_MUTED,
                    COLOR_SELECTED_BG if selected == logical_index else COLOR_SURFACE_ALT,
                )

    def draw_list_row(
        self, row, label, subtitle="", selected=False,
        icon=None, secondary_icon=None, trailing_text="",
    ):
        y = CONTENT_TOP + row * WIFI_ROW_HEIGHT
        background = COLOR_SELECTED_BG if selected else COLOR_SURFACE
        foreground = COLOR_SELECTED_TEXT if selected else COLOR_TEXT
        row_height = WIFI_ROW_HEIGHT - WIFI_ROW_BORDER_TRIM
        self.fill_rect(WIFI_LIST_X, y, WIFI_LIST_WIDTH, row_height, background)
        self.rect(
            WIFI_LIST_X, y, WIFI_LIST_WIDTH, row_height,
            COLOR_PRIMARY if selected else COLOR_BORDER,
        )
        if selected:
            self.fill_rect(
                WIFI_LIST_X, y, WIFI_ROW_SELECTED_STRIPE_WIDTH,
                row_height, COLOR_PRIMARY,
            )
        if icon:
            self.draw_asset(icon, WIFI_ICON_X, y + WIFI_ROW_ICON_Y_OFFSET)
        label_lines = self.text_lines(
            label, WIFI_LOCK_X - WIFI_NAME_X - WIFI_ROW_TEXT_GAP, 1
        )
        label_text = label_lines[0] if label_lines else ""
        self.text(
            label_text, WIFI_NAME_X, y + WIFI_ROW_LABEL_Y_OFFSET,
            foreground, background,
        )
        muted = COLOR_SELECTED_TEXT if selected else COLOR_TEXT_MUTED
        self.text(
            subtitle, WIFI_NAME_X, y + WIFI_ROW_SUBTITLE_Y_OFFSET,
            muted, background,
        )
        if secondary_icon:
            self.draw_asset(
                secondary_icon, WIFI_LOCK_X, y + WIFI_ROW_ICON_Y_OFFSET
            )
        if trailing_text:
            self.text(
                trailing_text, WIFI_SIGNAL_X, y + WIFI_ROW_ICON_Y_OFFSET,
                foreground, background,
            )

    def draw_loading(self, label, asset_name=ICONS["state"]["loading_message"]):
        self.begin_screen("Loading")
        self.draw_asset(asset_name, STATE_ART_X, STATE_ART_Y)
        self.draw_text_block(
            label, SCREEN_MARGIN, STATE_TEXT_Y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2,
        )
        self.draw_nav_bar()

    def show_error(self, asset_name, message_1="", message_2=""):
        self.begin_screen(message_1 or "Notice")
        if asset_name:
            self.draw_asset(asset_name, STATE_ART_X, STATE_ART_Y)
            text_y = STATE_TEXT_Y
        else:
            text_y = CONTENT_TOP + STATE_TEXT_FALLBACK_OFFSET_Y
        self.draw_text_block(
            message_2, SCREEN_MARGIN, text_y,
            SCREEN_WIDTH - SCREEN_MARGIN * 2, bottom=CONTENT_BOTTOM,
        )
        self.draw_nav_bar(
            center="Press", center_icon=ICONS["navigation"]["select"]
        )
