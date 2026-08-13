import time

from hardware_devices.input_device import Dial
from hardware_devices.storage import Storage


navigator_namespace = {}
exec(open("app/StateNavigator.py").read(), navigator_namespace)
StateNavigator = navigator_namespace["StateNavigator"]


RESULTS = []


def check(name, function):
    try:
        function()
        RESULTS.append(("PASS", name, ""))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


class State:
    def __init__(self):
        self.entered = 0
        self.exited = 0

    def enter_state(self):
        self.entered += 1

    def exit_state(self):
        self.exited += 1

    def handle_input(self, event, event_type=None):
        return

    def update(self):
        return

    def draw(self):
        return


class Encoder:
    def __init__(self, value):
        self.current = value

    def value(self):
        return self.current


def dial_event(previous, current):
    dial = Dial()
    dial.rotary_encoder = Encoder(current)
    dial.last_event_ms = time.ticks_add(time.ticks_ms(), -1000)
    dial.last_processed_encoder_value = previous
    dial.minimum_turn = 6
    dial.maximum_turn = 100
    return dial.event()


def test_manager():
    manager = StateNavigator(object())
    first = State()
    second = State()
    third = State()
    manager.start(first)
    if manager.current_state() is not first:
        raise RuntimeError("start rejected state")
    manager.push_state(second)
    manager.replace_state(third)
    if manager.current_state() is not third:
        raise RuntimeError("replace failed")
    if manager.pop_state() is not first:
        raise RuntimeError("pop failed")
    manager.pop_state()
    if manager.current_state() is not first:
        raise RuntimeError("root pop removed root")


def test_dial():
    if dial_event(0, 6) != 1:
        raise RuntimeError("positive movement rejected")
    if dial_event(6, 0) != -1:
        raise RuntimeError("negative movement rejected")
    if dial_event(995, 1) != 1:
        raise RuntimeError("wrapped movement rejected")


def test_storage():
    paths = ("./database/display.txt", "./database/preset.txt")
    originals = []
    for path in paths:
        file = open(path, "r")
        originals.append(file.read())
        file.close()
    try:
        storage = Storage()
        if storage.write_display_data("regression") is False:
            raise RuntimeError("display write returned False")
        if storage.read_display_data().get("message") != "regression":
            raise RuntimeError("display round trip failed")
        if storage.write_preset_data(["regression"]) is False:
            raise RuntimeError("preset write returned False")
        if storage.read_preset_data().get("presets") != ["regression"]:
            raise RuntimeError("preset round trip failed")
    finally:
        for index, path in enumerate(paths):
            file = open(path, "w")
            file.write(originals[index])
            file.close()


check("StateNavigator transitions", test_manager)
check("Dial threshold and wrap", test_dial)
check("Storage round trip and restore", test_storage)

for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

print("ESP32_REGRESSION_TESTS_COMPLETE")
