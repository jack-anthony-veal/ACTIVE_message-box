from config.config import MENU_VISIBLE_ROWS, visible_window


def menu_positions(total, selected, limit=MENU_VISIBLE_ROWS):
    start, end = visible_window(total, selected, limit)
    return tuple((item_index, item_index - start) for item_index in range(start, end))


class BaseScroll:
    def __init__(self, options, limit=MENU_VISIBLE_ROWS):
        if not options:
            raise ValueError("scroll options must not be empty")
        self.options = tuple(str(option) for option in options)
        self.length = len(self.options)
        self.limit = limit
        self.current_index = 0

    def setup(self):
        return self.refresh(0)

    def refresh(self, index=0):
        self.current_index = index % self.length
        return menu_positions(self.length, self.current_index, self.limit)

    __call__ = refresh
    scroll = refresh
