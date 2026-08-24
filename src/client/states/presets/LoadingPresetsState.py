from assets.registry import ICONS
from config.config import APP_FLAG_NON_FATAL_API, ERROR_HTTP_GET, ERROR_UNKNOWN
from states.presets.PresetMenu import PresetMenu
from states.NotifyState import ErrorState


class LoadingPresetsState:
    def __init__(self, app):
        self.app = app
        self.started = False

    def enter_state(self):
        self.draw()

    def exit_state(self):
        pass

    def handle_input(self, event, event_type=None):
        return

    def update(self):
        if self.started:
            return
        self.started = True

        try:
            success, presets = self.app.message_api.load_presets()
        except Exception as error:
            self.app.state_manager.replace_state(
                ErrorState(self.app, str(error), ERROR_HTTP_GET)
            )
            return

        if success and presets:
            self.app.state_manager.replace_state(PresetMenu(self.app, presets))
            return
        
        if not self.app.flags & APP_FLAG_NON_FATAL_API:
            self.app.flags |= APP_FLAG_NON_FATAL_API
            self.app.state_manager.replace_state(
                ErrorState(self.app, "Unable to load presets", ERROR_UNKNOWN)
            )
            return
            
        self.app.state_manager.replace_state(PresetMenu(self.app, ["unable to load", "check wifi conn", "unable to load"]))
        return

    def draw(self):
        self.app.display.draw_loading(
            "Loading presets", ICONS["state"]["loading_presets"]
        )
