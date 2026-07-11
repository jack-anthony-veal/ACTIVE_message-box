from states.PresetMenu import PresetMenu


class LoadingPresetsState:
    def __init__(self, app):
        self.app = app
        self.started = False

    def enter_state(self):
        self.draw()

    def exit_state(self):
        return

    def handle_input(self, event, event_type=None):
        return

    def update(self):
        if self.started:
            return

        self.started = True
        try:
            success, presets = self.app.message_api.load_presets()
        except Exception as error:
            self.app.state_manager.replace_state(ErrorState(self.app, str(error)))
            return

        if success and presets:
            self.app.state_manager.replace_state(PresetMenu(self.app, presets))
            return

        self.app.state_manager.replace_state(ErrorState(self.app, "Unable to load presets"))

    def draw(self):
        self.app.display.custom_message(
            "Loading presets",
            x_axis=0,
            y_axis=8,
            fill_all=True,
            wrap=False,
        )


class ErrorState:
    def __init__(self, app, message):
        self.app = app
        self.message = message

    def enter_state(self):
        self.draw()

    def exit_state(self):
        return

    def handle_input(self, event, event_type=None):
        return

    def update(self):
        return

    def draw(self):
        self.app.display.custom_message(
            self.message,
            x_axis=0,
            y_axis=8,
            fill_all=True,
            wrap=True,
        )
