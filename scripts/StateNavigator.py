class StateNavigator:
    def __init__(self, app):
        self.app = app
        self.state_object_current = None

    def push_state(self, state):
        ...

    def pop_state(self, state):
        ...

    def replace_state(self, state):
        ...

    def handle_input(self, state):
        ...

    def update_each_frame(self, state):
        ...

    def draw(self):
        ...

    def exit(self):
        ...