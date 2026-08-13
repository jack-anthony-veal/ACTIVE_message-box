"""Read-only/sequential ESP32 resource and hardware-load audit.

Run with: mpremote connect auto run device_tests/resource_audit.py
"""

import gc
import os
import time

# Current production config references three absent artwork constants.  Define
# inert audit-only fallbacks in builtins so unrelated modules can still be
# profiled without editing or copying production files onto the board.
import builtins
for _missing_art_name in ("MESSAGES_RUNS", "PRESETS_RUNS", "SETTINGS_RUNS"):
    if not hasattr(builtins, _missing_art_name):
        setattr(builtins, _missing_art_name, ())


def ticks_us():
    try:
        return time.ticks_us()
    except AttributeError:
        return int(time.time() * 1000000)


def ticks_diff(new, old):
    try:
        return time.ticks_diff(new, old)
    except AttributeError:
        return new - old


def emit(kind, name, detail):
    print(kind + " | " + name + " | " + str(detail))


def measure(name, operation, repeats=1):
    gc.collect()
    before = gc.mem_free()
    start = ticks_us()
    result = None
    try:
        for _ in range(repeats):
            result = operation()
        elapsed = ticks_diff(ticks_us(), start)
        middle = gc.mem_free()
        del result
        gc.collect()
        after = gc.mem_free()
        emit(
            "PROFILE",
            name,
            "runs=%d total_us=%d avg_us=%d live_delta=%d retained_delta=%d free=%d"
            % (repeats, elapsed, elapsed // repeats, middle - before, after - before, after),
        )
    except Exception as error:
        gc.collect()
        emit("FAIL", name, type(error).__name__ + ": " + str(error))


emit("INFO", "filesystem", os.listdir("/"))
gc.collect()
emit("INFO", "baseline_free_heap", gc.mem_free())


def import_app_modules():
    import states.BaseState


measure("imports.application_and_states", import_app_modules)

from app.StateNavigator import StateNavigator
from app.api import MessageApiClient
from hardware_devices.storage import Storage
from libraries.utils.text_tools import message_from_payload, wrap_text
from states.BaseState import BaseState
from states.LoadingMainMenuState import LoadingMainMenuState
from states.LoadingPresetsState import LoadingPresetsState
from states.MainMenuState import MainMenuCycleState
from states.NotifyState import Notify, add_text_to_box
from states.PresetInteract import PresetInteract, SendingState
from states.PresetMenu import PresetMenu


class NullDisplay:
    def power_on(self):
        return None

    def custom_message(self, *args, **kwargs):
        return None


class NullApi:
    def read_new_message(self):
        return False, {"message": None}

    def load_presets(self):
        return True, ["one", "two"]

    def send_preset(self, data):
        return True, None


class NullStorage:
    def read_display_data(self):
        return {"message": "saved"}

    def write_display_data(self, data):
        return True


class NullApp:
    def __init__(self):
        self.display = NullDisplay()
        self.message_api = NullApi()
        self.storage = NullStorage()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.safe_state = MainMenuCycleState(self, "safe")


app = NullApp()
constructors = (
    ("StateNavigator", lambda: StateNavigator(app)),
    ("MessageApiClient", MessageApiClient),
    ("Storage", Storage),
    ("BaseState", lambda: BaseState(app)),
    ("LoadingMainMenuState", lambda: LoadingMainMenuState(app)),
    ("LoadingPresetsState", lambda: LoadingPresetsState(app)),
    ("MainMenuCycleState", lambda: MainMenuCycleState(app, "preview")),
    ("Notify", lambda: Notify(app, "data", "title")),
    ("PresetInteract", lambda: PresetInteract(app, ["one"], 0)),
    ("SendingState", lambda: SendingState(app, "one")),
    ("PresetMenu", lambda: PresetMenu(app, ["one", "two"])),
)
for name, constructor in constructors:
    measure("construct." + name, constructor, 20)

measure("text.message_from_payload.dict", lambda: message_from_payload({"message": "hello"}), 200)
measure("text.message_from_payload.string", lambda: message_from_payload("hello"), 200)
measure("text.wrap.short", lambda: wrap_text("hello world", 16, 6), 200)
measure("text.wrap.long", lambda: wrap_text("0123456789" * 30, 16, 6), 50)
measure("notify.add_text_to_box", lambda: add_text_to_box("title", "data"), 200)
measure("storage.ensure_dict.string", lambda: Storage.ensure_dict("hello", "message"), 200)
measure("storage.ensure_dict.json", lambda: Storage.ensure_dict('{"message":"hello"}', "message"), 200)


def navigator_cycle():
    manager = StateNavigator(app)
    one = BaseState(app)
    two = BaseState(app)
    manager.start(one)
    manager.push_state(two)
    manager.pop_state()
    manager.replace_state(two)


measure("StateNavigator.transition_cycle", navigator_cycle, 100)


def menu_cycle():
    menu = MainMenuCycleState(app, "preview")
    menu.move_selection(1)
    menu.move_selection(-1)
    menu.draw()


measure("MainMenuCycleState.input_and_draw", menu_cycle, 100)


def preset_cycle():
    menu = PresetMenu(app, ["one", "two"])
    menu.handle_input(1, "dial")
    menu.draw()
    menu.preset_header()


measure("PresetMenu.input_and_draw", preset_cycle, 100)


def hardware_checks():
    from machine import I2C, Pin

    bus = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
    devices = bus.scan()
    emit("HARDWARE", "i2c_scan", devices)

    start = ticks_us()
    for _ in range(1000):
        Pin(23, Pin.IN, Pin.PULL_UP).value()
    emit("HARDWARE", "button_pin_1000_reads_us", ticks_diff(ticks_us(), start))

    from hardware_devices.input_device import Button, Dial

    button = Button()
    dial = Dial()
    start = ticks_us()
    for _ in range(1000):
        button.event()
        dial.event()
    elapsed = ticks_diff(ticks_us(), start)
    emit("HARDWARE", "input_poll_pair", "runs=1000 total_us=%d avg_us=%d" % (elapsed, elapsed // 1000))


measure("hardware.safe_checks", hardware_checks)
gc.collect()
emit("INFO", "final_free_heap", gc.mem_free())
print("RESOURCE_AUDIT_COMPLETE")
