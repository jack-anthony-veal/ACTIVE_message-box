from app.StateNavigator import StateNavigator
from states.LoadingMainMenuState import LoadingMainMenuState
from states.LoadingPresetsState import LoadingPresetsState
from states.MainMenuState import MainMenuCycleState
from states.NotifyState import ErrorState, Notify
from states.PresetInteract import PresetInteract, SendingState
from states.PresetMenu import PresetMenu


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

    def custom_message(self, *args, **kwargs):
        return


class Storage:
    def __init__(self):
        self.fail = False

    def read_display_data(self):
        if self.fail:
            raise OSError("storage failure")
        return {"message": "saved"}

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


def test_full_navigation():
    app = App()
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    main = app.state_manager.current_state()
    main.current_index = 1
    main.handle_input(True, "button")
    app.state_manager.update()
    preset = app.state_manager.current_state()
    preset.handle_input(True, "button")
    interaction = app.state_manager.current_state()
    if not isinstance(interaction, PresetInteract):
        raise RuntimeError("interaction state not reached")
    interaction.handle_input(True, "button")
    if not isinstance(app.state_manager.current_state(), LoadingMainMenuState):
        raise RuntimeError("back did not reset to loading state")


def test_storage_failure():
    app = App()
    app.storage.fail = True
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    if not isinstance(app.state_manager.current_state(), ErrorState):
        raise RuntimeError("error state was overwritten")


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
    notify.handle_input(True, "button")
    current = app.state_manager.current_state()
    if not isinstance(current, LoadingMainMenuState) or current is original or current.started:
        raise RuntimeError("reset did not create a fresh loader")


check("Full menu/preset/back navigation", test_full_navigation)
check("Loading storage failure recovery", test_storage_failure)
check("Sending false-result recovery", test_send_false)
check("Sending exception recovery", test_send_exception)
check("Notify fresh reset", test_notify_reset)

for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

print("ESP32_STATE_TESTS_COMPLETE")
