from config.config import IF_MESSAGE_NONE_DISP
from states.MainMenuState import MainMenuCycleState
from states.NotifyState import ErrorState


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
        if self.app.state_manager.current_state() is not self:
            return

        if self.started:
            return

        self.started = True
        message = None
        try:
            has_new_message, message = self.app.message_api.read_new_message()
            if has_new_message:
                self.app.storage.write_display_data(message)
            else:
                try:
                    message = self.app.storage.read_display_data().get("message")

                except Exception as storage_error:
                    self.app.state_manager.replace_state(state=ErrorState(self.app, str(storage_error), 22))
                    return

        except Exception as error:
            print("Message loading error:", error)
            self.app.state_manager.replace_state(state=ErrorState(self.app, str(error), 12))
            return

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
