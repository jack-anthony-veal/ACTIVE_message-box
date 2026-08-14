import importlib.util
import json
import os
import sys
import tempfile
import types


RESULTS = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, function):
    try:
        function()
        RESULTS.append(("PASS", name, ""))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


def load_module(name, relative_path):
    path = os.path.join(ROOT, relative_path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config_package = types.ModuleType("config")
config_package.__path__ = []
config = types.ModuleType("config.config")
config.SERVER_URL = "http://diagnostic.invalid"
config.TOKEN = "diagnostic"
config.PRESETS_JACK_URL = "http://diagnostic.invalid/presets"
config.NO_PRESETS_RESP = "No presets"
config.READ_ELLA_URL = "http://diagnostic.invalid/read"
config.SEND_JACK_URL = "http://diagnostic.invalid/send"
config_package.PRESETS_JACK_URL = config.PRESETS_JACK_URL
config_package.NO_PRESETS_RESP = config.NO_PRESETS_RESP
config_package.READ_ELLA_URL = config.READ_ELLA_URL
config_package.SEND_JACK_URL = config.SEND_JACK_URL
sys.modules["config"] = config_package
sys.modules["config.config"] = config
sys.modules["ujson"] = json


class Response:
    def __init__(self, status=200, text="{}", json_value=None, json_error=None):
        self.status_code = status
        self.text = text
        self.json_value = json_value
        self.json_error = json_error
        self.closed = False

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.json_value

    def close(self):
        self.closed = True


class Requests(types.ModuleType):
    def __init__(self):
        super().__init__("urequests")
        self.response = None
        self.error = None

    def get(self, *args, **kwargs):
        if self.error:
            raise self.error
        return self.response

    def post(self, *args, **kwargs):
        if self.error:
            raise self.error
        return self.response


requests = Requests()
sys.modules["urequests"] = requests
api_module = load_module("api_edge_test", "scripts/app/api.py")
api = api_module.MessageApiClient()


def test_api_closes_null_json():
    response = Response(200, "null", None)
    requests.response = response
    assert api.get_json("http://diagnostic.invalid") is None
    assert response.closed


def test_api_invalid_preset_shape():
    requests.response = Response(200, "[]", [])
    success, presets = api.load_presets()
    assert success is False
    assert type(presets) == list


def test_api_send_non_200_contract():
    requests.response = Response(500, "error", {})
    result = api.send_preset("test")
    assert type(result) == tuple
    assert len(result) == 2
    assert result[0] is False


def test_api_get_timeout_closes_or_has_no_response():
    requests.error = OSError("timeout")
    try:
        api.get_json("http://diagnostic.invalid")
    except OSError:
        return
    finally:
        requests.error = None
    raise AssertionError("timeout was silently accepted")


def test_storage_round_trip():
    with tempfile.TemporaryDirectory() as directory:
        config.DISPLAY_FILE = os.path.join(directory, "display.json")
        config.PRESET_FILE = os.path.join(directory, "preset.json")
        storage_module = load_module("storage_edge_test", "scripts/hardware_devices/storage.py")
        storage = storage_module.Storage()
        storage.write_display_data("hello")
        assert storage.read_display_data() == {"message": "hello"}
        storage.write_preset_data(["a", "b"])
        assert storage.read_preset_data() == {"presets": ["a", "b"]}


rotary_module = types.ModuleType("libraries.rotary_irq_esp")
rotary_module.RotaryIRQ = type("RotaryIRQ", (), {"RANGE_WRAP": 1})
sys.modules["libraries"] = types.ModuleType("libraries")
sys.modules["libraries.rotary_irq_esp"] = rotary_module
config.INPUT_DEBOUNCE_MS = 150
config.BUTTON_PRESS = 3
config.RIGHT_DIAL = 1
config.LEFT_DIAL = -1
config.DIAL_EVENT = 4
machine = types.ModuleType("machine")
machine.Pin = type("Pin", (), {"IN": 0, "PULL_UP": 1})
sys.modules["machine"] = machine
input_module = load_module("input_edge_test", "scripts/hardware_devices/input_device.py")


class Clock:
    now = 2000

    @classmethod
    def ticks_ms(cls):
        return cls.now

    @staticmethod
    def ticks_diff(new, old):
        return new - old


class Encoder:
    def __init__(self, value):
        self.current = value

    def value(self):
        return self.current


input_module.time = Clock


def dial_event(previous, current):
    dial = input_module.Dial.__new__(input_module.Dial)
    dial.rotary_encoder = Encoder(current)
    dial.last_event_ms = 0
    dial.last_processed_encoder_value = previous
    dial.minimum_turn = 6
    dial.maximum_turn = 100
    return dial.event()


def test_dial_positive():
    assert dial_event(0, 6) == 1


def test_dial_negative():
    assert dial_event(6, 0) == -1


def test_dial_wraparound():
    assert dial_event(995, 1) == 1


check("API closes response for null JSON", test_api_closes_null_json)
check("API handles non-dict preset response", test_api_invalid_preset_shape)
check("API send non-200 returns tuple", test_api_send_non_200_contract)
check("API timeout propagates", test_api_get_timeout_closes_or_has_no_response)
check("Storage round trip in temporary files", test_storage_round_trip)
check("Dial positive step", test_dial_positive)
check("Dial negative step", test_dial_negative)
check("Dial wraparound", test_dial_wraparound)


for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

failures = [result for result in RESULTS if result[0] == "FAIL"]
print("SUMMARY | passed=" + str(len(RESULTS) - len(failures)) + " failed=" + str(len(failures)))
sys.exit(1 if failures else 0)
