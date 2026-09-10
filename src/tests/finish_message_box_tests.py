import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
CLIENT = ROOT / "client"
sys.path.insert(0, str(CLIENT))


class Clock:
    now = 1000

    @classmethod
    def ticks_ms(cls):
        return cls.now

    @staticmethod
    def ticks_diff(new, old):
        return new - old

    @staticmethod
    def ticks_add(value, delta):
        return value + delta

    @classmethod
    def sleep_ms(cls, value):
        cls.now += value


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    IRQ_RISING = 4
    IRQ_FALLING = 8

    def __init__(self, number, *args, **kwargs):
        self.number = number

    def value(self):
        return 1

    def irq(self, *args, **kwargs):
        return


class WLAN:
    connected = False

    def __init__(self, interface):
        self.interface = interface

    def active(self, value=None):
        return True

    def isconnected(self):
        return self.connected

    def connect(self, *args):
        return

    def disconnect(self):
        return

    def scan(self):
        return []


def install_stubs():
    micropython = types.ModuleType("micropython")
    micropython.const = lambda value: value
    sys.modules.setdefault("micropython", micropython)
    machine = types.ModuleType("machine")
    machine.Pin = Pin
    machine.SPI = type("SPI", (), {"__init__": lambda self, *a, **k: None})
    machine.reset = lambda: None
    machine.reset_cause = lambda: 0
    machine.disable_irq = lambda: 0
    machine.enable_irq = lambda value: None
    for name, value in (("PWRON_RESET", 0), ("HARD_RESET", 1), ("WDT_RESET", 2),
                        ("DEEPSLEEP_RESET", 3), ("SOFT_RESET", 4)):
        setattr(machine, name, value)
    sys.modules.setdefault("machine", machine)
    network = types.ModuleType("network")
    network.STA_IF = 0
    network.WLAN = WLAN
    sys.modules.setdefault("network", network)
    sys.modules.setdefault("ujson", json)
    requests = types.ModuleType("urequests")
    requests.get = lambda *a, **k: None
    requests.post = lambda *a, **k: None
    sys.modules.setdefault("urequests", requests)
    st7789 = types.ModuleType("st7789")
    st7789.ST7789 = object
    sys.modules.setdefault("st7789", st7789)


install_stubs()

os.environ["MESSAGE_BOX_TOKEN"] = "test-shared-token"
host_spec = importlib.util.spec_from_file_location(
    "finish_message_box_host", ROOT / "host" / "main.py"
)
host = importlib.util.module_from_spec(host_spec)
host_spec.loader.exec_module(host)

from app.StateNavigator import StateNavigator
from app.updater import UpdateManager
import app.updater as updater_module
import app.ota_boot as ota_module
from hardware_devices.storage import Storage
import hardware_devices.storage as storage_module
from libraries.utils.timezone import format_uk_time
from states.message.message import MessageDisplay
from states.home.LoadingMainMenuState import LoadingMainMenuState
from states.home.MainMenuState import MainMenuCycleState
from states.presets.PresetInteract import PresetInteract, SendingState
from states.presets.PresetMenu import PresetMenu
from states.proc.two_mode import TwoModeController
from states.settings.settings_navigate import SettingsNav
from states.settings.WIFI import WifiState
from states.keyboard import Keyboard
import states.keyboard as keyboard_module
import libraries.utils.wifi as wifi_module
import start_up.tests as startup_module

keyboard_module.time = Clock
wifi_module.time = Clock


class RecordingDisplay:
    font_width = 8
    font_height = 16

    def __init__(self):
        self.calls = []

    def _call(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))

    def power_on(self):
        self._call("power_on")

    def measure_text(self, value):
        return len(str(value)) * 8

    def text_lines(self, value, max_width, max_lines=None):
        from libraries.utils.text_layout import layout_text

        return layout_text(value, max_width, self.measure_text, max_lines)

    def __getattr__(self, name):
        return lambda *args, **kwargs: self._call(name, *args, **kwargs)


class NullState:
    def enter_state(self):
        return

    def exit_state(self):
        return

    def handle_input(self, *args):
        return

    def update(self):
        return

    def draw(self):
        return


class FakeApi:
    def __init__(self):
        self.sent = []

    def send_message(self, text):
        self.sent.append(text)
        return True, None


class MemoryStorage:
    def __init__(self, message=None):
        self.message = message

    def newest_message(self):
        return self.message


class FakeApp:
    def __init__(self, message=None):
        self.display = RecordingDisplay()
        self.storage = MemoryStorage(message)
        self.message_api = FakeApi()
        self.state_manager = StateNavigator(self)
        self.reset_state = NullState()
        self.flags = 0


class HostMailboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        host.DATA = Path(self.temp.name)
        host.PRESETS_FILE = host.DATA / "presets.json"
        host.UPDATE_RESULTS_FILE = host.DATA / "update-results.json"
        host.SECRET = "test-shared-token"

    def tearDown(self):
        self.temp.cleanup()

    def test_non_destructive_read_and_id_matched_ack(self):
        first = host.send(
            "jack", host.Message(text="first"), "test-shared-token"
        )["message"]
        self.assertEqual(host.read("jack", "test-shared-token")["message"], first)
        self.assertEqual(host.read("jack", "test-shared-token")["message"], first)
        second = host.send(
            "jack", host.Message(text="second"), "test-shared-token"
        )["message"]
        self.assertFalse(
            host.acknowledge("jack", first["id"], "test-shared-token")["acknowledged"]
        )
        self.assertEqual(host.read("jack", "test-shared-token")["message"], second)
        self.assertTrue(
            host.acknowledge("jack", second["id"], "test-shared-token")["acknowledged"]
        )
        self.assertIsNone(host.read("jack", "test-shared-token")["message"])
        self.assertEqual(set(second), {"id", "sender", "text", "utc"})
        self.assertTrue(second["utc"].endswith("Z"))

    def test_zero_to_five_presets_and_long_detail(self):
        host.save_presets({"jack": [], "ella": []})
        self.assertEqual(host.load_presets()["jack"], [])
        long_text = "pixel wrapped " * 40
        for index in range(5):
            value = long_text + str(index)
            host.add_preset(
                "jack", host.Preset(text=value), "test-shared-token"
            )
        with self.assertRaises(host.HTTPException):
            host.add_preset(
                "jack", host.Preset(text="sixth"), "test-shared-token"
            )

    def test_bounded_update_results(self):
        old_limit = host.UPDATE_RESULTS_LIMIT
        host.UPDATE_RESULTS_LIMIT = 3
        try:
            for index in range(5):
                host.add_update_result(
                    host.UpdateResult(
                        device="jack", version=str(index), success=True
                    ),
                    "test-shared-token",
                )
            results = host.get_update_results("test-shared-token")["results"]
            self.assertEqual([item["version"] for item in results], ["2", "3", "4"])
        finally:
            host.UPDATE_RESULTS_LIMIT = old_limit


class StorageTests(unittest.TestCase):
    def test_jsonl_partial_tail_deduplicates_and_validates(self):
        old_messages = storage_module.MESSAGES_FILE
        try:
            with tempfile.TemporaryDirectory() as directory:
                storage_module.MESSAGES_FILE = os.path.join(directory, "messages.jsonl")
                first = {"id": "1", "sender": "ella", "text": "old", "utc": "2026-01-01T00:00:00Z"}
                with open(storage_module.MESSAGES_FILE, "wb") as output:
                    output.write((json.dumps(first) + "\n{partial").encode())
                storage = Storage()
                second = {"id": "2", "sender": "ella", "text": "new", "utc": "2026-01-01T01:00:00Z"}
                self.assertTrue(storage.append_message(second))
                self.assertTrue(storage.append_message(second))
                self.assertEqual([item["id"] for item in storage.read_messages()], ["1", "2"])
                self.assertEqual(storage.newest_message(), second)
        finally:
            storage_module.MESSAGES_FILE = old_messages

    def test_valid_final_line_without_newline_is_preserved(self):
        old_messages = storage_module.MESSAGES_FILE
        try:
            with tempfile.TemporaryDirectory() as directory:
                storage_module.MESSAGES_FILE = os.path.join(directory, "messages.jsonl")
                first = {"id": "1", "sender": "ella", "text": "old", "utc": "2026-01-01T00:00:00Z"}
                second = {"id": "2", "sender": "ella", "text": "new", "utc": "2026-01-01T01:00:00Z"}
                with open(storage_module.MESSAGES_FILE, "wb") as output:
                    output.write(json.dumps(first).encode())
                storage = Storage()
                storage.append_message(second)
                self.assertEqual([item["id"] for item in storage.read_messages()], ["1", "2"])
        finally:
            storage_module.MESSAGES_FILE = old_messages


class UiContractTests(unittest.TestCase):
    def test_controller_content_then_hidden_menu(self):
        controller = TwoModeController(2)
        self.assertFalse(controller.menu_open)
        self.assertIsNone(controller.activate())
        self.assertTrue(controller.menu_open)
        controller.rotate(1)
        self.assertEqual(controller.activate(), 1)
        self.assertFalse(controller.menu_open)

    def test_message_scroll_menu_and_keyboard_send_path(self):
        record = {
            "id": "1", "sender": "ella", "utc": "2026-07-01T12:00:00Z",
            "text": "long message words " * 80,
        }
        app = FakeApp(record)
        root = NullState()
        app.state_manager.start(root)
        state = MessageDisplay(app, record)
        app.state_manager.push_state(state)
        self.assertFalse(state.controller.menu_open)
        state.handle_input(1, 4)
        self.assertGreater(state.scroll_offset, 0)
        state.handle_input(True, 3)
        self.assertTrue(state.controller.menu_open)
        state.handle_input(True, 3)
        self.assertIsInstance(app.state_manager.current_state(), Keyboard)

    def test_preset_list_and_detail_use_two_modes_and_full_wrap(self):
        app = FakeApp()
        root = NullState()
        app.state_manager.start(root)
        menu = PresetMenu(app, ["one", "two"])
        app.state_manager.push_state(menu)
        menu.handle_input(True, 3)
        self.assertTrue(menu.controller.menu_open)
        menu.handle_input(True, 3)
        detail = app.state_manager.current_state()
        self.assertIsInstance(detail, PresetInteract)
        detail.send_data = "wrap me " * 100
        self.assertGreater(detail._max_scroll(), 0)

    def test_settings_back_pops_cleanly(self):
        app = FakeApp()
        root = NullState()
        app.state_manager.start(root)
        settings = SettingsNav(app)
        app.state_manager.push_state(settings)
        settings.handle_input(True, 3)
        settings.handle_input(1, 4)
        settings.handle_input(True, 3)
        self.assertIs(app.state_manager.current_state(), root)

    def test_wifi_status_renders_final_online_label(self):
        WLAN.connected = True
        app = FakeApp()
        state = WifiState(app)
        state._ssid = "test"
        state.enter_state()
        begin = [call for call in app.display.calls if call[0] == "begin_screen"]
        self.assertEqual(begin[-1][1][1], "Online")

    def test_failed_local_save_is_not_acknowledged_or_previewed(self):
        cached = {
            "id": "cached", "sender": "ella", "text": "safe copy",
            "utc": "2026-01-01T00:00:00Z",
        }

        class Api:
            acknowledgements = 0

            @staticmethod
            def read_new_message():
                return True, {"message": {
                    "id": "new", "sender": "ella", "text": "not saved",
                    "utc": "2026-01-01T01:00:00Z",
                }}

            @classmethod
            def acknowledge_message(cls, message_id):
                cls.acknowledgements += 1
                return True

        class FailedStorage:
            @staticmethod
            def append_message(message):
                return False

            @staticmethod
            def newest_message():
                return cached

        app = FakeApp()
        app.message_api = Api()
        app.storage = FailedStorage()
        loader = LoadingMainMenuState(app)
        app.state_manager.start(loader)
        app.state_manager.update()
        home = app.state_manager.current_state()
        self.assertIsInstance(home, MainMenuCycleState)
        self.assertEqual(home.message_record, cached)
        self.assertEqual(Api.acknowledgements, 0)

    def test_keyboard_special_keys_and_submit_in_both_cases(self):
        app = FakeApp()
        return_buffer = bytearray()
        destination = NullState()
        app.state_manager.start(NullState())
        keyboard = Keyboard(app, destination, return_buffer)
        app.state_manager.push_state(keyboard)
        keyboard.current = keyboard.alphabet.index("_")
        keyboard._handle_button()
        keyboard.current = keyboard.alphabet.index("£")
        keyboard._handle_button()
        keyboard._update_case()
        keyboard.current = keyboard.alphabet.index("<")
        keyboard._handle_button()
        self.assertEqual(keyboard.get_text(), " ")
        keyboard.current = keyboard.alphabet.index("~")
        keyboard._handle_button()
        self.assertEqual(return_buffer.decode("utf-8"), " ")
        self.assertIs(app.state_manager.current_state(), destination)


class TimeTests(unittest.TestCase):
    def test_uk_time_gmt_bst_and_boundaries(self):
        self.assertEqual(format_uk_time("2026-01-01T12:30:00Z"), "01/01/2026 12:30 GMT")
        self.assertEqual(format_uk_time("2026-07-01T12:30:00Z"), "01/07/2026 13:30 BST")
        self.assertEqual(format_uk_time("2026-03-29T00:59:00Z"), "29/03/2026 00:59 GMT")
        self.assertEqual(format_uk_time("2026-03-29T01:00:00Z"), "29/03/2026 02:00 BST")


class StartupTests(unittest.TestCase):
    def test_ordered_health_gate_and_offline_warning(self):
        class HealthyDisplay:
            width = 240
            height = 320

        class HealthyUpdater:
            @staticmethod
            def state():
                return {}

        class OfflineApi:
            @staticmethod
            def read_new_message():
                raise OSError("offline")

        originals = (
            startup_module.TOKEN,
            startup_module.DEVICE_OWNER,
            startup_module.DEVICE_PEER,
            startup_module.BASE_URL,
            startup_module.ERROR_LOG_FILE,
        )
        try:
            with tempfile.TemporaryDirectory() as directory:
                startup_module.TOKEN = "configured"
                startup_module.DEVICE_OWNER = "jack"
                startup_module.DEVICE_PEER = "ella"
                startup_module.BASE_URL = "http://example.invalid"
                startup_module.ERROR_LOG_FILE = os.path.join(directory, "errors.txt")
                WLAN.connected = False
                results = startup_module.run_startup_tests(
                    HealthyUpdater(),
                    "normal",
                    display_factory=HealthyDisplay,
                    input_factory=lambda: (object(), object()),
                    api=OfflineApi(),
                )
                self.assertEqual(
                    [result.name for result in results],
                    [
                        "Firmware", "ST7789 driver", "ST7789 configuration",
                        "Pin conflicts", "Display construction", "Heap",
                        "Free storage", "Temporary files", "Configuration",
                        "Log access", "Input construction", "Updater recovery",
                        "Wi-Fi/server",
                    ],
                )
                self.assertEqual(results[-1].status, "WARN")
                self.assertTrue(startup_module.emit_results(results))
        finally:
            (
                startup_module.TOKEN,
                startup_module.DEVICE_OWNER,
                startup_module.DEVICE_PEER,
                startup_module.BASE_URL,
                startup_module.ERROR_LOG_FILE,
            ) = originals


class FakeUpdateApi:
    def __init__(self, files):
        self.files = files

    def download_update_file(self, path):
        return self.files[path]


class UpdaterTests(unittest.TestCase):
    def manifest(self, files):
        return {
            "version": "9.0.0",
            "files": [
                {
                    "path": path,
                    "size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
                for path, data in files.items()
            ],
            "remove": [],
        }

    def test_stage_verify_apply_health_and_keep_backup(self):
        old_margin = updater_module.UPDATE_SPACE_MARGIN_BYTES
        updater_module.UPDATE_SPACE_MARGIN_BYTES = 0
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "app").mkdir()
                (root / "app" / "example.py").write_bytes(b"old")
                (root / "config").mkdir()
                (root / "config" / "device.ini").write_text("secret")
                files = {"app/example.py": b"new", "app/new.py": b"created"}
                manager = UpdateManager(directory)
                resets = []
                manager.install(
                    self.manifest(files), FakeUpdateApi(files), lambda: resets.append(True)
                )
                self.assertEqual((root / "app" / "example.py").read_bytes(), b"new")
                self.assertEqual((root / "config" / "device.ini").read_text(), "secret")
                self.assertEqual(manager.prepare_boot(), "first_boot")
                self.assertTrue(manager.mark_healthy())
                self.assertTrue(Path(manager.backup, "app", "example.py").is_file())
                self.assertEqual(resets, [True])
        finally:
            updater_module.UPDATE_SPACE_MARGIN_BYTES = old_margin

    def test_failed_first_boot_rolls_back(self):
        old_margin = updater_module.UPDATE_SPACE_MARGIN_BYTES
        updater_module.UPDATE_SPACE_MARGIN_BYTES = 0
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "app").mkdir()
                target = root / "app" / "example.py"
                target.write_bytes(b"old")
                files = {"app/example.py": b"bad-new"}
                manager = UpdateManager(directory)
                manager.install(self.manifest(files), FakeUpdateApi(files), lambda: None)
                self.assertEqual(manager.prepare_boot(), "first_boot")
                self.assertEqual(manager.prepare_boot(), "rolled_back")
                self.assertEqual(target.read_bytes(), b"old")
        finally:
            updater_module.UPDATE_SPACE_MARGIN_BYTES = old_margin

    def test_preserved_and_traversal_paths_are_rejected(self):
        manager = UpdateManager(".")
        data = b"x"
        for path in ("config/device.ini", "database/messages.jsonl", "../boot.py"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                manager._validate_manifest(self.manifest({path: data}))

    def test_partial_apply_is_restored_immediately(self):
        old_margin = updater_module.UPDATE_SPACE_MARGIN_BYTES
        original_rename = updater_module.os.rename
        updater_module.UPDATE_SPACE_MARGIN_BYTES = 0
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "app").mkdir()
                for name in ("one.py", "two.py"):
                    (root / "app" / name).write_bytes(("old-" + name).encode())
                files = {"app/one.py": b"new-one", "app/two.py": b"new-two"}

                def fail_second_staged_rename(source, destination):
                    if ".update-stage" in source and source.endswith("two.py"):
                        raise OSError("simulated apply interruption")
                    return original_rename(source, destination)

                updater_module.os.rename = fail_second_staged_rename
                manager = UpdateManager(directory)
                with self.assertRaises(OSError):
                    manager.install(self.manifest(files), FakeUpdateApi(files), lambda: None)
                self.assertEqual((root / "app/one.py").read_bytes(), b"old-one.py")
                self.assertEqual((root / "app/two.py").read_bytes(), b"old-two.py")
                self.assertEqual(manager.state()["status"], "rolled_back")
        finally:
            updater_module.os.rename = original_rename
            updater_module.UPDATE_SPACE_MARGIN_BYTES = old_margin

    def test_first_boot_arms_reset_timer_until_health_confirmation(self):
        machine = sys.modules["machine"]
        original_manager = ota_module.UpdateManager
        original_timer = getattr(machine, "Timer", None)
        original_reset = machine.reset
        resets = []

        class FirstBootManager:
            @staticmethod
            def prepare_boot():
                return "first_boot"

        class Timer:
            ONE_SHOT = 1
            latest = None

            def __init__(self, timer_id):
                self.deinitialised = False
                Timer.latest = self

            def init(self, period, mode, callback):
                self.period = period
                self.mode = mode
                self.callback = callback

            def deinit(self):
                self.deinitialised = True

        try:
            ota_module.UpdateManager = FirstBootManager
            machine.Timer = Timer
            machine.reset = lambda: resets.append(True)
            self.assertEqual(ota_module.begin(), "first_boot")
            self.assertEqual(Timer.latest.period, 30000)
            Timer.latest.callback(Timer.latest)
            self.assertEqual(resets, [True])
            ota_module.cancel_timer()
            self.assertTrue(Timer.latest.deinitialised)
        finally:
            ota_module.UpdateManager = original_manager
            if original_timer is None:
                del machine.Timer
            else:
                machine.Timer = original_timer
            machine.reset = original_reset


class PackageTests(unittest.TestCase):
    def test_package_contains_assets_but_not_runtime_data_or_credentials(self):
        spec = importlib.util.spec_from_file_location(
            "package_update", REPOSITORY / "tools" / "package_update.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            manifest = module.package("2.0.0", CLIENT, Path(directory) / "update")
            paths = {entry["path"] for entry in manifest["files"]}
            self.assertIn("assets/bin/navigation/back_24x24.bin", paths)
            self.assertIn("config/version.py", paths)
            self.assertNotIn("config/device.ini", paths)
            self.assertFalse(any(path.startswith("database/") for path in paths))
            for stable_path in (
                "boot.py", "app/__init__.py", "app/ota_boot.py", "app/updater.py"
            ):
                self.assertNotIn(stable_path, paths)

    def test_bad_main_is_rolled_back_by_stable_bootstrap(self):
        old_margin = updater_module.UPDATE_SPACE_MARGIN_BYTES
        updater_module.UPDATE_SPACE_MARGIN_BYTES = 0
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "main.py").write_text("old main\n")
                files = {"main.py": b"raise ImportError('broken update')\n"}
                manager = UpdateManager(directory)
                manager.install(
                    UpdaterTests().manifest(files),
                    FakeUpdateApi(files),
                    lambda: None,
                )
                self.assertEqual(manager.prepare_boot(), "first_boot")
                self.assertEqual(manager.state()["status"], "checking")
                self.assertEqual(manager.prepare_boot(), "rolled_back")
                self.assertEqual((root / "main.py").read_text(), "old main\n")
        finally:
            updater_module.UPDATE_SPACE_MARGIN_BYTES = old_margin


if __name__ == "__main__":
    unittest.main(verbosity=2)
