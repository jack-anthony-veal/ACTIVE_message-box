import importlib.util
import json
import os
import sys
import tempfile
import types


RESULTS = []


def check(name, function):
    try:
        function()
        RESULTS.append(("PASS", name, ""))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_micropython_stubs():
    micropython = types.ModuleType("micropython")
    micropython.const = lambda value: value
    sys.modules["micropython"] = micropython

    framebuf = types.ModuleType("framebuf")
    framebuf.MONO_VLSB = 0
    framebuf.FrameBuffer = type("FrameBuffer", (), {"__init__": lambda self, *args, **kwargs: None})
    sys.modules["framebuf"] = framebuf

    machine = types.ModuleType("machine")

    class Pin:
        IN = 0
        OUT = 1
        PULL_UP = 2
        IRQ_RISING = 4
        IRQ_FALLING = 8

        def __init__(self, *args, **kwargs):
            pass

        def value(self):
            return 1

        def irq(self, *args, **kwargs):
            pass

    machine.Pin = Pin
    machine.I2C = type("I2C", (), {"__init__": lambda self, *args, **kwargs: None})
    machine.disable_irq = lambda: 0
    machine.enable_irq = lambda state: None
    sys.modules["machine"] = machine
    network = types.ModuleType("network")
    network.STA_IF = 0
    network.WLAN = lambda interface: type("WLAN", (), {"isconnected": lambda self: True})()
    sys.modules["network"] = network
    sys.modules["ujson"] = json
    sys.modules["urequests"] = types.ModuleType("urequests")


install_micropython_stubs()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

from app.StateNavigator import StateNavigator
from states.LoadingMainMenuState import LoadingMainMenuState
from states.LoadingPresetsState import LoadingPresetsState
from states.MainMenuState import MainMenuCycleState
from states.NotifyState import ErrorState, Notify, add_text_to_box
import states.NotifyState as notify_state_module
from states.PresetInteract import PresetInteract, SendingState
from states.PresetMenu import PresetMenu
from libraries.utils.text_tools import message_from_payload, wrap_text

notify_state_module.time.ticks_ms = lambda: 1000
notify_state_module.time.ticks_diff = lambda new, old: new - old


class Display:
    def __init__(self):
        self.calls = []

    def power_on(self):
        self.calls.append(("power_on",))

    def custom_message(self, *args, **kwargs):
        self.calls.append(("custom_message", args, kwargs))

    def show_error(self, *args, **kwargs):
        self.calls.append(("show_error", args, kwargs))


class Storage:
    def __init__(self):
        self.message = "saved message"
        self.raise_read = False
        self.raise_write = False
        self.writes = []

    def read_display_data(self):
        if self.raise_read:
            raise OSError("storage read failed")
        return {"message": self.message}

    def write_display_data(self, data):
        if self.raise_write:
            raise OSError("storage write failed")
        self.writes.append(data)


class Api:
    def __init__(self):
        self.message = (False, {"message": None})
        self.message_error = None
        self.presets = (True, ["one", "two"])
        self.preset_error = None
        self.send = (True, None)
        self.send_error = None

    def read_new_message(self):
        if self.message_error:
            raise self.message_error
        return self.message

    def load_presets(self):
        if self.preset_error:
            raise self.preset_error
        return self.presets

    def send_preset(self, data):
        if self.send_error:
            raise self.send_error
        return self.send


class App:
    def __init__(self):
        self.display = Display()
        self.storage = Storage()
        self.message_api = Api()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.safe_state = MainMenuCycleState(self, "safe")


def test_state_manager():
    app = App()
    loading = LoadingMainMenuState(app)
    app.state_manager.start(loading)
    app.state_manager.update()
    assert isinstance(app.state_manager.current_state(), MainMenuCycleState)
    preset = PresetMenu(app, ["one"])
    app.state_manager.push_state(preset)
    preset.handle_input(True, 3)
    assert isinstance(app.state_manager.current_state(), PresetInteract)
    app.state_manager.current_state().handle_input(True, 3)
    assert isinstance(app.state_manager.current_state(), LoadingMainMenuState)


def test_fresh_reset():
    app = App()
    old = LoadingMainMenuState(app)
    app.state_manager.start(old)
    old.started = True
    notify = Notify(app, "ok", "done")
    app.state_manager.replace_state(notify)
    notify.handle_input(True, 3)
    current = app.state_manager.current_state()
    assert isinstance(current, LoadingMainMenuState)
    assert current is not old
    assert current.started is False


def test_loading_storage_failure():
    app = App()
    app.storage.raise_read = True
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    assert isinstance(app.state_manager.current_state(), ErrorState)


def test_loading_presets_failure():
    app = App()
    app.message_api.preset_error = OSError("timeout")
    app.state_manager.start(LoadingPresetsState(app))
    app.state_manager.update()
    assert isinstance(app.state_manager.current_state(), ErrorState)


def test_sending_success():
    app = App()
    app.state_manager.start(MainMenuCycleState(app, "message"))
    app.state_manager.push_state(SendingState(app, "one"))
    assert isinstance(app.state_manager.current_state(), Notify)


def test_sending_false_result():
    app = App()
    app.message_api.send = (False, "rejected")
    app.state_manager.start(MainMenuCycleState(app, "message"))
    app.state_manager.push_state(SendingState(app, "one"))
    assert isinstance(app.state_manager.current_state(), ErrorState)


def test_sending_exception():
    app = App()
    app.message_api.send_error = OSError("timeout")
    app.state_manager.start(MainMenuCycleState(app, "message"))
    app.state_manager.push_state(SendingState(app, "one"))
    assert isinstance(app.state_manager.current_state(), ErrorState)


def test_notify_exception_data():
    app = App()
    Notify(app, OSError("bad"), "error").enter_state()


def test_menu_navigation():
    app = App()
    menu = MainMenuCycleState(app, "message")
    menu.move_selection(1)
    assert menu.current_index == 1
    menu.move_selection(-1)
    assert menu.current_index == 0
    menu.move_selection(-1)
    assert menu.current_index == len(menu.options) - 1


def test_preset_navigation():
    app = App()
    menu = PresetMenu(app, ["one", "two"])
    menu.handle_input(1, 4)
    assert menu.current_index_preset == 1
    assert menu.preset_data_select == "two"
    menu.handle_input(1, 4)
    assert menu.current_index_preset == 0


def test_text_tools():
    assert message_from_payload({"message": "hello"}) == "hello"
    assert message_from_payload(None) == "No new messages!"
    assert wrap_text("123456789", width=4, max_lines=3) == ["1234", "5678", "9"]


def test_notification_box():
    result = add_text_to_box("title", "data")
    assert len(result) == 2


check("StateNavigator push/pop/replace", test_state_manager)
check("StateNavigator reset creates fresh loader", test_fresh_reset)
check("LoadingMainMenu storage failure remains ErrorState", test_loading_storage_failure)
check("LoadingPresets API failure becomes ErrorState", test_loading_presets_failure)
check("Sending success becomes Notify", test_sending_success)
check("Sending false result becomes ErrorState", test_sending_false_result)
check("Sending exception becomes ErrorState", test_sending_exception)
check("Notify accepts exception data", test_notify_exception_data)
check("Main menu navigation wraps", test_menu_navigation)
check("Preset navigation wraps", test_preset_navigation)
check("Text conversion and wrapping", test_text_tools)
check("Notification box formatting", test_notification_box)


for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

failures = [result for result in RESULTS if result[0] == "FAIL"]
print("SUMMARY | passed=" + str(len(RESULTS) - len(failures)) + " failed=" + str(len(failures)))
sys.exit(1 if failures else 0)
