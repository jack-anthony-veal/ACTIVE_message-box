# === State Navigator ===
# Responsible for calling and effecting other states where all states inherit a specific instance of App()
from states.MainMenuState import MainMenuCycleState
# TODO: add a boot state and a loading state
# TODO: add a context manager here or for an app
#  TODO: add push and close and other functionality


class StateNavigator():
    def __init__(self, app):
        self.app = app
        self._state_stack = []
        self.previous_state = None
        self.second_state_prior = None
        self.next_state = None
        self.running = False

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
        self.push_state(state)

    # ENTER A STATE
    def push_state(self, state):
        self._state_stack.append(state)
        state.enter_state() # Add object context

    # EXIT A STATE and ENTER prior
    def pop_state(self):
        current = self.current_state()
        if current is None:
            return None
        current.exit_state()
        self._state_stack.pop()
        current = self.current_state()
        if current is not None:
            current.enter_state()
        return current

    def reset(self):
        self.current_state.exit()
        self.current_state = MainMenuCycleState(self.app)
        self.current_state.enter_state()


    # EXIT A STATE and ENTER prior
    # TODO: consider using replace for better menu navigation
    def replace_state(self, state): # changes working state without exit
        current = self.current_state()
        if current is not None:
            current.exit_state()
            self._state_stack.pop()
        self._state_stack.append(state)
        state.enter_state()

    # calls the state to handle input
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



