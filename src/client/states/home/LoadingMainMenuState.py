from assets.registry import ICONS
from config.config import APP_FLAG_NON_FATAL_API, APP_FLAG_NON_FATAL_STORAGE
from states.home.MainMenuState import MainMenuCycleState


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
        if self.started or self.app.state_manager.current_state() is not self:
            return
        self.started = True
        newest = None
        try:
            has_new_message, payload = self.app.message_api.read_new_message()
            if has_new_message:
                message = payload["message"]
                append = getattr(self.app.storage, "append_message", None)
                saved = (
                    append(message)
                    if append is not None
                    else self.app.storage.write_display_data(payload)
                )
                if saved is not False:
                    print("MESSAGE|saved|{}".format(message["id"]))
                    acknowledge = getattr(
                        self.app.message_api, "acknowledge_message", None
                    )
                    if acknowledge is not None and acknowledge(message["id"]):
                        print("MESSAGE|acked|{}".format(message["id"]))
                    elif acknowledge is not None:
                        print("WARNING|message_ack_pending|{}".format(message["id"]))
                    newest_method = getattr(self.app.storage, "newest_message", None)
                    newest = newest_method() if newest_method is not None else message
                else:
                    print("WARNING|message_save|{}".format(message["id"]))
        except Exception as error:
            self.app.flags |= APP_FLAG_NON_FATAL_API
            print("WARNING|message_sync|{}".format(error))

        if newest is None:
            try:
                newest_method = getattr(self.app.storage, "newest_message", None)
                if newest_method is not None:
                    newest = newest_method()
                else:
                    saved = self.app.storage.read_display_data()
                    newest = saved.get("record", saved.get("message"))
            except Exception as error:
                self.app.flags |= APP_FLAG_NON_FATAL_STORAGE
                print("WARNING|message_storage|{}".format(error))

        self.app.state_manager.replace_state(MainMenuCycleState(self.app, newest))

    def draw(self):
        self.app.display.power_on()
        self.app.display.draw_loading(
            "Loading messages", ICONS["state"]["loading_message"]
        )
