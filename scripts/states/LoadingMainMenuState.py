from config.config import IF_MESSAGE_NONE_DISP
from states.MainMenuState import MainMenuCycleState


class LoadingMainMenuState:
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
        message = None
        try:
            has_new_message, message = self.app.message_api.read_new_message()
            if has_new_message:
                self.app.storage.write_display_data(message)
            else:
                message = self.app.storage.read_display_data().get("message")
        except Exception as error:
            print("Message loading error:", error)
            message = self.app.storage.read_display_data().get("message")

        if message is None:
            message = IF_MESSAGE_NONE_DISP

        self.app.state_manager.replace_state(MainMenuCycleState(self.app, message))

    def draw(self):
        self.app.display.power_on()
        self.app.display.custom_message(
            "Loading messages",
            x_axis=0,
            y_axis=8,
            fill_all=True,
            wrap=False,
        )
