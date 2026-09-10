from app.StateNavigator import StateNavigator
from states.home.LoadingMainMenuState import LoadingMainMenuState
from states.presets.LoadingPresetsState import LoadingPresetsState
from states.home.MainMenuState import MainMenuCycleState
from states.NotifyState import ErrorState, Notify
from states.presets.PresetInteract import PresetInteract, SendingState
from states.presets.PresetMenu import PresetMenu
from config.config import (
    APP_FLAG_NON_FATAL_STORAGE, BUTTON_PRESS, DIAL_EVENT,
)


RESULTS = []


def check(name, function):
    try:
        function()
        RESULTS.append(("PASS", name, ""))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


class Display:
    def power_on(self):
        return

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class Storage:
    def __init__(self):
        self.fail = False

    def read_display_data(self):
        if self.fail:
            raise OSError("storage failure")
        return {"message": "saved"}

    def newest_message(self):
        if self.fail:
            raise OSError("storage failure")
        return {
            "id": "saved", "sender": "ella", "text": "saved",
            "utc": "2026-01-01T00:00:00Z",
        }

    def write_display_data(self, data):
        return


class Api:
    def __init__(self):
        self.send_result = (True, None)
        self.send_error = None
        self.preset_error = None

    def read_new_message(self):
        return False, {"message": None}

    def load_presets(self):
        if self.preset_error:
            raise self.preset_error
        return True, ["one", "two"]

    def send_preset(self, data):
        if self.send_error:
            raise self.send_error
        return self.send_result


class App:
    def __init__(self):
        self.display = Display()
        self.storage = Storage()
        self.message_api = Api()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.safe_state = MainMenuCycleState(self, "safe")
        self.flags = 0


def test_full_navigation():
    app = App()
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    main = app.state_manager.current_state()
    main.current_index = 1
    main.handle_input(True, BUTTON_PRESS)
    app.state_manager.update()
    preset = app.state_manager.current_state()
    preset.handle_input(True, BUTTON_PRESS)
    preset.handle_input(True, BUTTON_PRESS)
    interaction = app.state_manager.current_state()
    if not isinstance(interaction, PresetInteract):
        raise RuntimeError("interaction state not reached")
    interaction.handle_input(True, BUTTON_PRESS)
    interaction.handle_input(1, DIAL_EVENT)
    interaction.handle_input(True, BUTTON_PRESS)
    if not isinstance(app.state_manager.current_state(), PresetMenu):
        raise RuntimeError("back did not pop to preset list")


def test_storage_failure():
    app = App()
    app.storage.fail = True
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    if not isinstance(app.state_manager.current_state(), MainMenuCycleState):
        raise RuntimeError("offline Home was not reached")
    if not app.flags & APP_FLAG_NON_FATAL_STORAGE:
        raise RuntimeError("storage warning flag was not set")


def test_send_false():
    app = App()
    app.message_api.send_result = (False, "rejected")
    app.state_manager.start(MainMenuCycleState(app, "message"))
    app.state_manager.push_state(SendingState(app, "one"))
    if not isinstance(app.state_manager.current_state(), ErrorState):
        raise RuntimeError("send failure did not become ErrorState")


def test_send_exception():
    app = App()
    app.message_api.send_error = OSError("timeout")
    app.state_manager.start(MainMenuCycleState(app, "message"))
    app.state_manager.push_state(SendingState(app, "one"))
    if not isinstance(app.state_manager.current_state(), ErrorState):
        raise RuntimeError("send exception did not become ErrorState")


def test_notify_reset():
    app = App()
    original = LoadingMainMenuState(app)
    app.state_manager.start(original)
    original.started = True
    notify = Notify(app, "ok", "done")
    app.state_manager.replace_state(notify)
    notify.handle_input(True, BUTTON_PRESS)
    current = app.state_manager.current_state()
    if not isinstance(current, LoadingMainMenuState) or current is original or current.started:
        raise RuntimeError("reset did not create a fresh loader")


check("Full menu/preset/back navigation", test_full_navigation)
check("Loading storage failure reaches offline Home", test_storage_failure)
check("Sending false-result recovery", test_send_false)
check("Sending exception recovery", test_send_exception)
check("Notify fresh reset", test_notify_reset)

for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

print("ESP32_STATE_TESTS_COMPLETE")
