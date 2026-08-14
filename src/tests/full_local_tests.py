"""Deterministic CPython tests for MicroPython application logic."""

import importlib
import io
import json
import os
import sys
import tempfile
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


class FakeClock:
    now = 1000

    @classmethod
    def ticks_ms(cls):
        return cls.now

    @staticmethod
    def ticks_diff(new, old):
        return new - old

    @staticmethod
    def sleep_ms(value):
        FakeClock.now += value

    @staticmethod
    def sleep(value):
        FakeClock.now += int(value * 1000)


class FakePin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    IRQ_RISING = 4
    IRQ_FALLING = 8
    values = {}

    def __init__(self, number, *args, **kwargs):
        self.number = number
        self.handler = None
        FakePin.values.setdefault(number, 1)

    def value(self, value=None):
        if value is not None:
            FakePin.values[self.number] = value
        return FakePin.values[self.number]

    def irq(self, trigger=None, handler=None):
        self.handler = handler


class FakeI2C:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def scan(self):
        return [0x3C]

    def writeto(self, *args):
        self.calls.append(("writeto", args))

    def writeto_mem(self, *args):
        self.calls.append(("writeto_mem", args))


class FakeFrameBuffer:
    def __init__(self, buffer, width, height, format):
        self.buffer = buffer
        self.width = width
        self.height = height
        self.calls = []

    def _call(self, name, *args):
        self.calls.append((name, args))

    def fill(self, *args): self._call("fill", *args)
    def text(self, *args): self._call("text", *args)
    def hline(self, *args): self._call("hline", *args)
    def rect(self, *args): self._call("rect", *args)
    def fill_rect(self, *args): self._call("fill_rect", *args)


class FakeWLAN:
    connected = True

    def __init__(self, interface):
        self.interface = interface

    def isconnected(self): return self.connected
    def active(self, value=None): return True
    def disconnect(self): return None
    def connect(self, *args): return None
    def scan(self): return []


class FakeResponse:
    def __init__(self, status=200, payload=None, text=""):
        self.status_code = status
        self.payload = payload
        self.text = text
        self.closed = False

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload

    def close(self):
        self.closed = True


class FakeRequests(types.ModuleType):
    def __init__(self):
        super().__init__("urequests")
        self.response = FakeResponse(payload={})
        self.error = None
        self.calls = []

    def _request(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))
        if self.error:
            raise self.error
        return self.response

    def get(self, *args, **kwargs): return self._request("get", *args, **kwargs)
    def post(self, *args, **kwargs): return self._request("post", *args, **kwargs)


requests = FakeRequests()


def install_stubs():
    micropython = types.ModuleType("micropython")
    micropython.const = lambda value: value
    sys.modules["micropython"] = micropython

    framebuf = types.ModuleType("framebuf")
    framebuf.MONO_VLSB = 0
    framebuf.FrameBuffer = FakeFrameBuffer
    sys.modules["framebuf"] = framebuf

    machine = types.ModuleType("machine")
    machine.Pin = FakePin
    machine.I2C = FakeI2C
    machine.disable_irq = lambda: 0
    machine.enable_irq = lambda state: None
    machine.reset = lambda: None
    machine.deepsleep = lambda *args: None
    machine.reset_cause = lambda: 0
    for name, value in (("PWRON_RESET", 0), ("HARD_RESET", 1), ("WDT_RESET", 2),
                        ("DEEPSLEEP_RESET", 3), ("SOFT_RESET", 4)):
        setattr(machine, name, value)
    sys.modules["machine"] = machine

    network = types.ModuleType("network")
    network.STA_IF = 0
    network.WLAN = FakeWLAN
    sys.modules["network"] = network

    esp32 = types.ModuleType("esp32")
    esp32.NVS = object
    esp32.WAKEUP_ALL_LOW = 0
    esp32.wake_on_ext1 = lambda **kwargs: None
    sys.modules["esp32"] = esp32

    esp = types.ModuleType("esp")
    esp.osdebug = lambda value: None
    sys.modules["esp"] = esp
    sys.modules["ujson"] = json
    sys.modules["urequests"] = requests


install_stubs()

from app.StateNavigator import StateNavigator
from app.api import MessageApiClient
from hardware_devices.display_device import OledDisplay
from hardware_devices.input_device import Button, Dial
from hardware_devices.storage import Storage
from libraries.utils import ascii as artwork
from libraries.utils.text_tools import message_from_payload, wrap_text
from states.LoadingMainMenuState import LoadingMainMenuState
from states.LoadingPresetsState import LoadingPresetsState
from states.MainMenuState import MainMenuCycleState
from states.NotifyState import ErrorState, Notify, add_text_to_box
from states.PresetInteract import PresetInteract, SendingState
from states.PresetMenu import PresetMenu
import hardware_devices.input_device as input_module

input_module.time = FakeClock


class RecordingDisplay:
    def __init__(self): self.calls = []
    def power_on(self): self.calls.append(("power_on", (), {}))
    def custom_message(self, *args, **kwargs): self.calls.append(("custom_message", args, kwargs))
    def show_error(self, *args, **kwargs): self.calls.append(("show_error", args, kwargs))


class FakeStorage:
    def __init__(self):
        self.message = {"message": "stored"}
        self.writes = []
    def read_display_data(self): return self.message
    def write_display_data(self, value): self.writes.append(value); return value


class FakeApi:
    def __init__(self):
        self.message_result = (False, {"message": None})
        self.preset_result = (True, ["one", "two"])
        self.send_result = (True, None)
        self.read_calls = self.preset_calls = self.send_calls = 0
    def read_new_message(self): self.read_calls += 1; return self.message_result
    def load_presets(self): self.preset_calls += 1; return self.preset_result
    def send_preset(self, data): self.send_calls += 1; return self.send_result


class FakeApp:
    def __init__(self):
        self.display = RecordingDisplay()
        self.storage = FakeStorage()
        self.message_api = FakeApi()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.safe_state = MainMenuCycleState(self, "safe")
        self.preset_state = LoadingPresetsState(self)
        self.preset_interact = None


class State:
    def __init__(self): self.events = []; self.entered = self.exited = self.updated = self.drawn = 0
    def enter_state(self): self.entered += 1
    def exit_state(self): self.exited += 1
    def handle_input(self, *args): self.events.append(args)
    def update(self): self.updated += 1
    def draw(self): self.drawn += 1


class TestImportsAndConfig(unittest.TestCase):
    def test_all_normal_modules_import(self):
        modules = []
        for base, dirs, files in os.walk(SCRIPTS):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".idea")]
            for filename in files:
                if filename.endswith(".py") and filename not in ("boot.py", "main.py"):
                    rel = os.path.relpath(os.path.join(base, filename), SCRIPTS)[:-3]
                    if rel != "__init__" and not rel.endswith(".__init__"):
                        modules.append(rel.replace(os.sep, "."))
        for name in modules:
            with self.subTest(module=name):
                importlib.import_module(name)

    def test_app_constructs_with_fakes(self):
        from app.app import App
        app = App()
        self.assertIsNotNone(app.state_manager)


class TestNavigator(unittest.TestCase):
    def test_transitions_and_forwarding(self):
        manager = StateNavigator(object())
        first, second, third = State(), State(), State()
        manager.start(first)
        manager.push_state(second)
        manager.replace_state(third)
        manager.handle_input(1, "dial")
        manager.update(); manager.draw()
        self.assertEqual(third.events, [(1, "dial")])
        self.assertEqual((third.updated, third.drawn), (1, 1))
        self.assertIs(manager.pop_state(), first)
        self.assertIs(manager.pop_state(), first)

    def test_empty_stack_is_safe(self):
        manager = StateNavigator(object())
        manager.handle_input(None); manager.update(); manager.draw()
        self.assertIsNone(manager.pop_state())


class TestApi(unittest.TestCase):
    def setUp(self):
        requests.calls.clear(); requests.error = None
        self.api = MessageApiClient()

    def test_get_json_closes_success_and_parse_failure(self):
        for payload in ({"message": "ok"}, ValueError("bad json")):
            response = FakeResponse(payload=payload, text="raw")
            requests.response = response
            self.api.get_json("http://test")
            self.assertTrue(response.closed)

    def test_get_json_network_failure(self):
        requests.error = OSError("offline")
        with self.assertRaises(OSError): self.api.get_json("http://test")

    def test_get_json_http_failure_closes_response(self):
        response = FakeResponse(status=500, payload={"message": "wrong"})
        requests.response = response
        with self.assertRaises(OSError): self.api.get_json("http://test")
        self.assertTrue(response.closed)

    def test_read_message_contract(self):
        for payload, expected in (({"message": "hello"}, True), ({"message": None}, False), ([], False)):
            requests.response = FakeResponse(payload=payload)
            success, data = self.api.read_new_message()
            self.assertEqual(success, expected)
            self.assertIsInstance(data, dict)

    def test_presets_validate_shape(self):
        for payload, expected in (({"presets": ["a"]}, True), ({"presets": []}, True),
                                  ({"presets": "bad"}, False), (None, False), ([], False)):
            requests.response = FakeResponse(payload=payload)
            success, presets = self.api.load_presets()
            self.assertEqual(success, expected)
            self.assertIsInstance(presets, (list, tuple))

    def test_send_contract_body_and_close(self):
        for status, expected in ((200, True), (500, False)):
            response = FakeResponse(status=status)
            requests.response = response
            success, detail = self.api.send_preset("hello")
            self.assertEqual(success, expected)
            self.assertTrue(response.closed)
            call = requests.calls[-1]
            self.assertEqual(json.loads(call[2]["data"]), {"text": "hello"})

    def test_send_network_failure(self):
        requests.error = OSError("offline")
        success, detail = self.api.send_preset("hello")
        self.assertFalse(success)


class TestStates(unittest.TestCase):
    def test_message_loader_calls_once_and_falls_back(self):
        app = FakeApp(); state = LoadingMainMenuState(app)
        app.state_manager.start(state); state.update(); state.update()
        self.assertEqual(app.message_api.read_calls, 1)
        self.assertIsInstance(app.state_manager.current_state(), MainMenuCycleState)

    def test_preset_loader_once_success_empty_failure(self):
        for result, expected_type in (((True, ["one"]), PresetMenu), ((True, []), ErrorState),
                                      ((False, ["fallback"]), ErrorState)):
            app = FakeApp(); app.message_api.preset_result = result
            state = LoadingPresetsState(app); app.state_manager.start(state)
            state.update(); state.update()
            self.assertEqual(app.message_api.preset_calls, 1)
            self.assertIsInstance(app.state_manager.current_state(), expected_type)

    def test_main_menu_navigation_and_redraw(self):
        app = FakeApp(); menu = MainMenuCycleState(app, "message")
        app.state_manager.start(menu)
        initial = len(app.display.calls)
        menu.draw(); self.assertEqual(len(app.display.calls), initial)
        menu.handle_input(1, 4); menu.draw()
        self.assertEqual(menu.current_index, 1)
        menu.handle_input(-1, 4); self.assertEqual(menu.current_index, 0)
        menu.handle_input(-1, 4); self.assertEqual(menu.current_index, len(menu.options) - 1)

    def test_reopening_presets_uses_fresh_loader(self):
        app = FakeApp(); menu = MainMenuCycleState(app, "message")
        app.state_manager.start(menu); menu.current_index = 1
        menu.handle_input(True, 3)
        first = app.state_manager.current_state()
        first.update()
        app.state_manager.start(menu); menu.current_index = 1
        menu.handle_input(True, 3)
        second = app.state_manager.current_state()
        self.assertIsInstance(second, LoadingPresetsState)
        self.assertIsNot(first, second)
        second.update()
        self.assertEqual(app.message_api.preset_calls, 2)

    def test_preset_navigation_and_select(self):
        app = FakeApp(); menu = PresetMenu(app, ["one", "two"])
        app.state_manager.start(menu)
        menu.handle_input(1, 4); self.assertEqual(menu.preset_data_select, "two")
        menu.handle_input(1, 4); self.assertEqual(menu.preset_data_select, "one")
        menu.handle_input(True, 3)
        self.assertIsInstance(app.state_manager.current_state(), PresetInteract)

    def test_send_exactly_once_and_transitions(self):
        for result, expected in (((True, None), Notify), ((False, "rejected"), ErrorState)):
            app = FakeApp(); app.message_api.send_result = result
            app.state_manager.start(SendingState(app, "one"))
            app.state_manager.current_state().draw()
            self.assertEqual(app.message_api.send_calls, 1)
            self.assertIsInstance(app.state_manager.current_state(), expected)

    def test_error_state_draws_and_recovers(self):
        app = FakeApp(); state = ErrorState(app, OSError("bad"), 22)
        app.state_manager.start(state)
        self.assertEqual(len([c for c in app.display.calls if c[0] == "show_error"]), 1)
        state.handle_input(True, 3)
        self.assertIsInstance(app.state_manager.current_state(), LoadingMainMenuState)


class TestDisplayTextArtwork(unittest.TestCase):
    def test_text_payloads_and_wrapping(self):
        self.assertEqual(message_from_payload({"message": "hello"}), "hello")
        self.assertEqual(message_from_payload(None), "No new messages!")
        self.assertEqual(wrap_text("123456789", 4, 3), ["1234", "5678", "9"])
        self.assertEqual(wrap_text("a\nb", 4, 3), ["a", "b"])

    def test_notification_text_accepts_non_strings(self):
        title, data = add_text_to_box(OSError("title"), 123)
        self.assertIsInstance(title, str); self.assertIsInstance(data, str)

    def test_artwork_runs_are_valid(self):
        names = [name for name in dir(artwork) if name.isupper()]
        checked = 0
        for name in names:
            value = getattr(artwork, name)
            if not isinstance(value, (bytes, bytearray)):
                continue
            checked += 1
            self.assertEqual(len(value) % 3, 0, name)
            for index in range(0, len(value), 3):
                y, x, length = value[index:index + 3]
                self.assertLessEqual(y, 63, name); self.assertLessEqual(x, 127, name)
                self.assertGreater(length, 0, name); self.assertLessEqual(x + length, 128, name)
        self.assertGreater(checked, 10)

    def test_oled_coordinates_and_show_count(self):
        display = OledDisplay()
        display.custom_message("hello", x_axis=0, y_axis=8, fill_all=True, wrap=True)
        calls = display.oled.calls
        texts = [args for name, args in calls if name == "text"]
        self.assertTrue(texts)
        for text, x, y, colour in texts:
            self.assertGreaterEqual(x, 0); self.assertLessEqual(x, 127)
            self.assertGreaterEqual(y, 0); self.assertLessEqual(y, 63)


class TestInputStorage(unittest.TestCase):
    def test_button_debounce_and_rearm(self):
        FakeClock.now = 1000; FakePin.values[23] = 1
        button = Button(); FakeClock.now += 200; FakePin.values[23] = 0
        self.assertTrue(button.event()); self.assertIsNone(button.event())
        FakePin.values[23] = 1; self.assertIsNone(button.event())
        FakeClock.now += 200; FakePin.values[23] = 0; self.assertTrue(button.event())

    def test_dial_direction_wrap_and_event_type(self):
        FakeClock.now = 1000; dial = Dial(); FakeClock.now += 300
        dial.last_processed_encoder_value = 0; dial.rotary_encoder._value = 4
        self.assertEqual(dial.event(), 1); self.assertEqual(dial.event_type, 4)
        FakeClock.now += 300; dial.last_processed_encoder_value = 4; dial.rotary_encoder._value = 0
        self.assertEqual(dial.event(), -1)
        FakeClock.now += 300; dial.last_processed_encoder_value = 998; dial.rotary_encoder._value = 1
        self.assertEqual(dial.event(), 1)

    def test_storage_round_trip_and_malformed_fallback(self):
        import hardware_devices.storage as storage_module
        old_display, old_preset = storage_module.DISPLAY_FILE, storage_module.PRESET_FILE
        try:
            with tempfile.TemporaryDirectory() as directory:
                storage_module.DISPLAY_FILE = os.path.join(directory, "display.txt")
                storage_module.PRESET_FILE = os.path.join(directory, "preset.txt")
                storage = Storage()
                storage.write_display_data("hello")
                self.assertEqual(storage.read_display_data(), {"message": "hello"})
                storage.write_preset_data(["a", "b"])
                self.assertEqual(storage.read_preset_data(), {"presets": ["a", "b"]})
                with open(storage_module.DISPLAY_FILE, "w") as handle: handle.write("{bad")
                self.assertEqual(storage.read_display_data(), {"message": "{bad"})
        finally:
            storage_module.DISPLAY_FILE, storage_module.PRESET_FILE = old_display, old_preset


if __name__ == "__main__":
    unittest.main(verbosity=2)
