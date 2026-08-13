from states.presets.PresetMenu import PresetMenu
from states.NotifyState import ErrorState
_OTHER = 1 << 0
_NON_FATAL_API = 1 << 1
_NON_FATAL_WIFI= 1 << 2
_NON_FATAL_HTTP= 1 << 3
_NON_FATAL = 1 << 4
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
            self.app.state_manager.replace_state(ErrorState(self.app, str(error), 12))
            return

        if success and presets:
            self.app.state_manager.replace_state(PresetMenu(self.app, presets))
            return
        
        if not self.app.flags & _NON_FATAL_API:
            self.app.flags |= _NON_FATAL_API
            self.app.state_manager.replace_state(ErrorState(self.app, "Unable to load presets", 0))
            return
            
        self.app.state_manager.replace_state(PresetMenu(self.app, ["unable to load", "check wifi conn", "unable to load"]))
        return

    def draw(self):
        self.app.display.custom_message(
            "Loading presets",
            x_axis=0,
            y_axis=8,
            fill_all=True,
            wrap=False,
        )


