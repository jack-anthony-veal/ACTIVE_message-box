class StateNavigator:
    def __init__(self, app):
        self.app = app
        self._state_stack = []
        self.start_state = None

    def __setattr__(self, name, value):
        if name == "current_state":
            if self.current_state() is value:
                return
            raise AttributeError("Use StateNavigator transition methods")
        object.__setattr__(self, name, value)

    def current_state(self):
        if not self._state_stack:
            return None
        return self._state_stack[-1]

    @property
    def current_state_check(self):
        return self.current_state()

    def start(self, state):
        current = self.current_state()
        if current is not None:
            current.exit_state()
        self._state_stack = []
        self.start_state = state
        self.push_state(state)

    def push_state(self, state):
        current = self.current_state()
        if current is not None:
            current.exit_state()
        self._state_stack.append(state)
        state.enter_state()

    def pop_state(self):
        current = self.current_state()
        if current is None:
            return None
        if len(self._state_stack) <= 1:
            return current
        current.exit_state()
        self._state_stack.pop()
        current = self.current_state()
        if current is not None:
            current.enter_state()
        return current

    def reset(self):
        state = self.start_state.__class__(self.app)
        self.start(state)

    def replace_state(self, state):
        current = self.current_state()
        if current is not None:
            current.exit_state()
            self._state_stack.pop()

        self._state_stack.append(state)
        state.enter_state()

    def handle_input(self, event, event_type=None):
        current = self.current_state()
        if current is not None:
            current.handle_input(event, event_type)

    def update(self):
        current = self.current_state()
        if current is not None:
            current.update()

    def draw(self):
        current = self.current_state()
        if current is not None:
            current.draw()
