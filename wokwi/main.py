import time
import network
import ujson

from app.app import App
from app.updater import UpdateManager, _join, _mkdirs, _remove_tree, _write_json
from hardware_devices.display_device import Display
from hardware_devices.storage import Storage
from states.home.LoadingMainMenuState import LoadingMainMenuState
from states.home.MainMenuState import MainMenuCycleState
from app.runtime import confirm_healthy, startup


class SerialDisplayBackend:
    def fill(self, *args):
        return

    def pixel(self, *args):
        return

    def line(self, *args):
        return

    def hline(self, *args):
        return

    def vline(self, *args):
        return

    def rect(self, *args):
        return

    def fill_rect(self, *args):
        return

    def text(self, *args):
        return

    def blit_buffer(self, *args):
        return

    def on(self):
        return

    def off(self):
        return

    def sleep_mode(self, *args):
        return


class OfflineApi:
    def read_new_message(self):
        raise OSError("simulated offline")


class SimulatorApi:
    def __init__(self, storage):
        self.storage = storage
        self.reads = 0
        self.ack_saved_first = False

    def read_new_message(self):
        self.reads += 1
        if self.reads > 1:
            return False, {"message": None}
        return True, {
            "message": {
                "id": "wokwi-message-002",
                "sender": "ella",
                "utc": "2026-09-07T12:30:00Z",
                "text": "This is a deliberately long simulator message. " * 18,
            }
        }

    def acknowledge_message(self, message_id):
        self.ack_saved_first = self.storage.has_message(message_id)
        return self.ack_saved_first

    def load_presets(self):
        return True, ["One", "A preset long enough to wrap across several pixel lines."]

    def send_message(self, text):
        return True, {"text": text}

    def report_update_result(self, version, success, detail, device):
        return {"saved": True}

    def get_update_manifest(self):
        return {"version": "0.1.0", "files": []}


def connect_guest():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    if not station.isconnected():
        station.connect("Wokwi-GUEST", "")
        for _ in range(100):
            if station.isconnected():
                break
            time.sleep_ms(100)
    print("WOKWI|wifi|{}".format("connected" if station.isconnected() else "offline"))


def rollback_probe():
    root = "sim-ota"
    _remove_tree(root)
    manager = UpdateManager(root)
    _mkdirs(_join(root, "app"))
    _mkdirs(_join(manager.backup, "app"))
    with open(_join(root, "app/example.py"), "w") as output:
        output.write("new")
    with open(_join(manager.backup, "app/example.py"), "w") as output:
        output.write("old")
    _write_json(manager.state_file, {
        "status": "checking",
        "version": "failed-test",
        "files": ["app/example.py"],
        "remove": [],
        "backed_up": ["app/example.py"],
    })
    status = manager.prepare_boot()
    with open(_join(root, "app/example.py"), "r") as source:
        restored = source.read()
    if status != "rolled_back" or restored != "old":
        raise RuntimeError("rollback probe failed")
    print("SCENARIO|failed_update_rollback|PASS")


def prepare_message_file(storage):
    first = {
        "id": "wokwi-message-001",
        "sender": "ella",
        "utc": "2026-01-07T12:00:00Z",
        "text": "Cached while offline",
    }
    with open("database/messages.jsonl", "wb") as output:
        output.write((ujson.dumps(first) + "\n{partial").encode("utf-8"))
    if storage.newest_message()["id"] != first["id"]:
        raise RuntimeError("partial JSONL recovery failed")
    print("SCENARIO|partial_final_line|PASS")


def main():
    connect_guest()
    updater = UpdateManager()
    api_for_startup = SimulatorApi(Storage())
    started = startup(
        updater=updater,
        display_factory=lambda: Display(backend=SerialDisplayBackend()),
        api=api_for_startup,
    )
    if started is None:
        print("SCENARIO|startup|FAIL")
        return
    print("SCENARIO|startup|PASS")
    rollback_probe()

    storage = Storage()
    prepare_message_file(storage)
    app = App(
        message_api=OfflineApi(),
        display=Display(backend=SerialDisplayBackend()),
        storage=storage,
        updater=updater,
    )
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    if not isinstance(app.state_manager.current_state(), MainMenuCycleState):
        raise RuntimeError("offline recovery did not reach Home")
    print("SCENARIO|offline_recovery|PASS")

    api = SimulatorApi(storage)
    app.message_api = api
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    if not api.ack_saved_first:
        raise RuntimeError("message was ACKed before validated local save")
    if len([m for m in storage.read_messages() if m["id"] == "wokwi-message-002"]) != 1:
        raise RuntimeError("message deduplication failed")
    print("SCENARIO|local_log_ack_order|PASS")
    confirm_healthy(updater)
    print("STARTUP|HOME_READY")

    while True:
        button_event = app.button.event()
        if button_event is not None:
            app.state_manager.handle_input(button_event, app.button.event_type)
        dial_event = app.dial.event()
        if dial_event is not None:
            app.state_manager.handle_input(dial_event, app.dial.event_type)
        app.state_manager.update()
        app.state_manager.draw()
        time.sleep_ms(2)


main()
