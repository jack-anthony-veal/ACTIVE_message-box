from config.ui_config import MENU_VISIBLE_ROWS, visible_window


def menu_positions(total, selected, limit=MENU_VISIBLE_ROWS):
    start, end = visible_window(total, selected, limit)
    return tuple((item_index, item_index - start) for item_index in range(start, end))


class BaseMenu:
    def __init__(self, display, opts):
        if not isinstance(opts, list) or not opts:
            raise ValueError("menu options must be a non-empty list")
        self.display = display
        self.options = [str(option) for option in opts]
        self.option_selected = None

    def setup(self):
        self.refresh_menu()

    def reset(self, fill=False):
        if fill:
            self.display.fill()
        self.option_selected = None

    def refresh_menu(self, index=None, icons=False):
        if index is not None and not isinstance(index, int):
            raise TypeError("menu index must be int or None")
        if index is not None and not 0 <= index < len(self.options):
            raise IndexError("menu index out of range")
        self.option_selected = index
        icon_names = {
            "back": "nav_back",
            "change": "nav_change_edit",
            "choose": "nav_enter_select",
            "edit": "nav_change_edit",
            "enter": "nav_enter_select",
            "refresh": "action_refresh_scan",
            "scan": "action_refresh_scan",
            "send": "nav_send",
        }

        if len(self.options) == 1:
            right = self.options[0]
            self.display.draw_nav_bar(
                right=right,
                selected=2 if index == 0 else None,
                right_icon=icon_names.get(right.lower()),
            )
            return

        left = self.options[1]
        right = self.options[0]
        self.display.draw_nav_bar(
            left=left,
            right=right,
            selected=(2 if index == 0 else 0) if index is not None else None,
            left_icon=icon_names.get(left.lower()),
            right_icon=icon_names.get(right.lower()),
        )

    refresh = refresh_menu


class BaseScroll:
    def __init__(self, display, options):
        if not options:
            raise ValueError("scroll options must not be empty")
        self.display = display
        self.options = tuple(str(option) for option in options)
        self.length = len(self.options)
        self.current_index = 0

    def setup(self):
        self.refresh(0)

    def refresh(self, index=0):
        self.current_index = index % self.length
        self.display.begin_screen("Settings", "Rotate")
        icons = {
            "account": "menu_account",
            "device": "menu_device",
            "wifi": "menu_wifi",
            "graphics": "menu_graphics",
            "tbd": "action_question",
        }
        for item_index, row_index in menu_positions(self.length, self.current_index):
            option = self.options[item_index]
            icon_name = icons.get(option.lower(), "action_question")
            self.display.draw_menu_row(
                row_index,
                option,
                selected=item_index == self.current_index,
                icon=icon_name,
                selected_icon=icon_name + "_selected",
            )

    scroll = refresh
