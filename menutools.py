from config import config as _config

_MENU_Y_AXIS = getattr(_config, "MENU_Y_AXIS", 54)

_DISPLAY_WIDTH = 128
_DISPLAY_HEIGHT = 64
_MENU_HEIGHT = _DISPLAY_HEIGHT - _MENU_Y_AXIS
_MENU_SPLIT_X = 64


class MenuTools:
    def __init__(self, app):
        self.app = app

    def _draw_menu_opts_corners(self, change_x=0, back_x=_MENU_SPLIT_X):
        oled = self.app.display.oled
        y_top = _MENU_Y_AXIS
        y_bottom = _DISPLAY_HEIGHT - 1

        # Dotted horizontal edges.
        for x in range(change_x, _DISPLAY_WIDTH, 4):
            length = 2 if x + 1 < _DISPLAY_WIDTH else 1
            oled.hline(x, y_top, length, 1)
            oled.hline(x, y_bottom, length, 1)

        # Dotted left edge, centre divider, and right edge.
        for y in range(y_top, _DISPLAY_HEIGHT, 2):
            oled.vline(change_x, y, 1, 1)
            oled.vline(back_x - 1, y, 1, 1)
            oled.vline(_DISPLAY_WIDTH - 1, y, 1, 1)

    def _draw_selected(self, index_selected=None, option_one="", option_two=""):
        if not option_one or not option_two:
            return

        oled = self.app.display.oled
        option_one = str(option_one)[:6]
        option_two = str(option_two)[:6]

        # Clear the complete menu strip first.
        oled.fill_rect(0, _MENU_Y_AXIS, _DISPLAY_WIDTH, _MENU_HEIGHT, 0)

        left_background = 1 if index_selected == 0 else 0
        right_background = 1 if index_selected == 1 else 0

        if left_background:
            oled.fill_rect(0, _MENU_Y_AXIS, _MENU_SPLIT_X, _MENU_HEIGHT, 1)

        if right_background:
            oled.fill_rect(
                _MENU_SPLIT_X,
                _MENU_Y_AXIS,
                _DISPLAY_WIDTH - _MENU_SPLIT_X,
                _MENU_HEIGHT,
                1,
            )

        oled.text(
            option_one,
            1,
            _MENU_Y_AXIS + 1,
            0 if left_background else 1,
        )
        oled.text(
            option_two,
            _MENU_SPLIT_X + 1,
            _MENU_Y_AXIS + 1,
            0 if right_background else 1,
        )

        # Draw the border last so fills cannot erase it.
        self._draw_menu_opts_corners()

