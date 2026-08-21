class MenuTools:
    def __init__(self, app):
        self.app = app

    def _draw_menu_opts_corners(self, change_x=0, back_x=0):
        return

    def _draw_selected(self, index_selected=None, option_one="", option_two=""):
        if not option_one or not option_two:
            return
        icons = {
            "back": "nav_back",
            "change": "nav_change_edit",
            "edit": "nav_change_edit",
            "enter": "nav_enter_select",
            "refresh": "action_refresh_scan",
            "scan": "action_refresh_scan",
            "send": "nav_send",
        }
        left = str(option_two)
        right = str(option_one)
        self.app.display.draw_nav_bar(
            left=left,
            right=right,
            selected=(2 if index_selected == 0 else 0)
            if index_selected is not None else None,
            left_icon=icons.get(left.lower()),
            right_icon=icons.get(right.lower()),
        )
