class BaseState:
    def __init__(self, app):
        self.app = app

    def enter_state(self):
        ...

    def exit_state(self):
        ...

    def handle_input(self):
        ...

    def update_each_frame(self):
        ...

    def draw(self):
        ...