class TwoModeController:
    CONTENT = 0
    MENU = 1

    def __init__(self, action_count):
        if action_count < 1:
            raise ValueError("action_count must be positive")
        self.action_count = action_count
        self.mode = self.CONTENT
        self.action_index = 0

    @property
    def menu_open(self):
        return self.mode == self.MENU

    def show_menu(self, selected=0):
        self.mode = self.MENU
        self.action_index = selected % self.action_count

    def hide_menu(self):
        self.mode = self.CONTENT
        self.action_index = 0

    def rotate(self, direction):
        if not self.menu_open:
            return False
        self.action_index = (self.action_index + direction) % self.action_count
        return True

    def activate(self):
        if not self.menu_open:
            self.show_menu()
            return None
        selected = self.action_index
        self.hide_menu()
        return selected
