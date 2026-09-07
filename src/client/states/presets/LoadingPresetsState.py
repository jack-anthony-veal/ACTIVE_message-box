from assets.registry import ICONS
from config.config import APP_FLAG_NON_FATAL_API, MAX_PRESETS
from states.presets.PresetMenu import PresetMenu


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
        presets = []
        try:
            success, remote_presets = self.app.message_api.load_presets()
            if success:
                presets = list(remote_presets)[:MAX_PRESETS]
                cache = getattr(self.app.storage, "write_preset_data", None)
                if cache is not None:
                    cache(presets)
            else:
                raise OSError("invalid preset response")
        except Exception as error:
            self.app.flags |= APP_FLAG_NON_FATAL_API
            print("WARNING|preset_sync|{}".format(error))
            try:
                load_cache = getattr(self.app.storage, "read_preset_data", None)
                presets = load_cache().get("presets", []) if load_cache else []
            except Exception:
                presets = []
        self.app.state_manager.replace_state(PresetMenu(self.app, presets[:MAX_PRESETS]))

    def draw(self):
        self.app.display.draw_loading(
            "Loading presets", ICONS["state"]["loading_presets"]
        )
