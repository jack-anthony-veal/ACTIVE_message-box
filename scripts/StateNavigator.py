# === State Navigator ===
# Responsible for calling and effecting other states where all states inherit a specific instance of App()
# TODO: add a boot state and a loading state
# TODO: add a context manager here or for an app
#  TODO: add push and close and other functionality



class StateNavigator:
    def __init__(self, app):
        self.app = app
        self.current_state = None
        self.previous_state = None
        self.second_state_prior = None
        self.next_state = None

    @property
    def current_state_check(self):
        return self.current_state

    # ENTER A STATE
    def push_state(self, state):
        if self.current_state is not None:
            self.current_state.exit_state()

        self.current_state = state # Add object context
        self.current_state.enter_state() # Enter the state

    # EXIT A STATE and ENTER prior
    def pop_state(self):
        self.current_state.exit_state() # exit

        # enter prior or remain # TODO: exception or pop up for return with no prior
        self.current_state = self.previous_state if self.current_state is not None else self.current_state
        self.current_state.enter_state()


    # EXIT A STATE and ENTER prior
    # TODO: consider using replace for better menu navigation
    def replace_state(self, state): # changes working state without exit
        self.current_state = state
        state.enter_state(state)

    # calls the state to handle input
    def handle_input(self, event, event_type):
        self.current_state.handle_input(event, event_type)

    def update(self):
        self.current_state.update()

    def draw(self):
        self.current_state.draw()

    def exit(self):
        self.current_state.exit()