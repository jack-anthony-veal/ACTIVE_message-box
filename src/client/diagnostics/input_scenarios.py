import time

from app.app import App
from config.config import (
    BUTTON_PRESS, DIAL_EVENT, KEYBOARD_DOUBLE_PRESS_MS,
)
from main import recover_runtime_error, run_iteration
from states.NotifyState import ErrorState, Notify
from states.home.LoadingMainMenuState import LoadingMainMenuState
from states.home.MainMenuState import MainMenuCycleState
from states.keyboard import Keyboard
from states.message.message import MessageDisplay
from states.presets.PresetInteract import PresetInteract
from states.presets.PresetMenu import PresetMenu
from states.settings.WIFI import WifiState
from states.settings.settings_navigate import SettingsNav
from states.settings.wifi_settings import WifiSettings


class ScenarioApi:
    def __init__(self):
        self.sent = []

    def read_new_message(self):
        return False, {"message": None}

    def acknowledge_message(self, message_id):
        return True

    def load_presets(self):
        return True, [
            "First preset",
            "Second preset with enough text to exercise wrapping and scrolling " * 8,
        ]

    def send_message(self, text):
        self.sent.append(str(text))
        return True, None


class ScenarioStorage:
    def __init__(self, message):
        self.message = message
        self.presets = []

    def newest_message(self):
        return self.message

    def read_preset_data(self):
        return {"presets": list(self.presets)}

    def write_preset_data(self, presets):
        self.presets = list(presets)
        return True


class MalformedApi(ScenarioApi):
    def read_new_message(self):
        return True, {"old_server_shape": "ignored"}


class ScenarioInput:
    def __init__(self, event, event_type):
        self._event = event
        self.event_type = event_type

    def event(self):
        return self._event


class BrokenState:
    def enter_state(self):
        return

    def exit_state(self):
        return

    def handle_input(self, event, event_type=None):
        raise RuntimeError("simulated input failure")

    def update(self):
        return

    def draw(self):
        return


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def state_name(app):
    state = app.state_manager.current_state()
    return "None" if state is None else state.__class__.__name__


def require_state(app, state_type, marker):
    require(
        isinstance(app.state_manager.current_state(), state_type),
        marker + " got=" + state_name(app),
    )
    print("INPUT_SCENARIO|PASS|" + marker)


def input_event(app, event, event_type):
    app.state_manager.handle_input(event, event_type)
    app.state_manager.update()
    app.state_manager.draw()


def start_home(app, message):
    app.state_manager.start(MainMenuCycleState(app, message))
    require_state(app, MainMenuCycleState, "home")


def select_keyboard_key(app, character):
    keyboard = app.state_manager.current_state()
    require(isinstance(keyboard, Keyboard), "keyboard expected")
    movement = keyboard.alphabet.index(character) - keyboard.current
    input_event(app, movement, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    time.sleep_ms(KEYBOARD_DOUBLE_PRESS_MS + 10)
    app.state_manager.update()


def messages_scenario(app, message):
    print("INPUT_SCENARIO|START|messages")
    start_home(app, message)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MessageDisplay, "messages_open")
    input_event(app, 1, DIAL_EVENT)
    input_event(app, -1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MainMenuCycleState, "messages_back")

    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, Keyboard, "message_keyboard")
    select_keyboard_key(app, "a")
    select_keyboard_key(app, "~")
    require_state(app, Notify, "message_sent")
    require(app.message_api.sent[-1] == "a", "message send payload")


def empty_messages_scenario(app, message):
    print("INPUT_SCENARIO|START|empty_messages")
    app.storage.message = None
    start_home(app, None)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MessageDisplay, "empty_messages_open")
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MainMenuCycleState, "empty_messages_back")
    app.storage.message = message


def presets_scenario(app, message):
    print("INPUT_SCENARIO|START|presets")
    start_home(app, message)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, PresetMenu, "presets_open")
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, PresetInteract, "preset_detail")
    input_event(app, 1, DIAL_EVENT)
    input_event(app, -1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, PresetMenu, "preset_back")

    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, PresetInteract, "preset_detail_reopen")
    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, Notify, "preset_sent")


def settings_scenario(app, message):
    print("INPUT_SCENARIO|START|settings")
    start_home(app, message)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, SettingsNav, "settings_open")
    input_event(app, 2, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, WifiState, "wifi_status")
    input_event(app, True, BUTTON_PRESS)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, SettingsNav, "wifi_back")
    input_event(app, True, BUTTON_PRESS)
    input_event(app, 1, DIAL_EVENT)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MainMenuCycleState, "settings_back")


def wifi_list_scenario(app, message):
    print("INPUT_SCENARIO|START|wifi_list")
    start_home(app, message)
    app.state_manager.push_state(WifiSettings(app))
    require_state(app, WifiSettings, "wifi_list")
    state = app.state_manager.current_state()
    state.networks = []
    state.current_index = None
    state.controller.hide_menu()
    input_event(app, True, BUTTON_PRESS)
    input_event(app, True, BUTTON_PRESS)
    require_state(app, MainMenuCycleState, "wifi_list_back")


def malformed_data_scenario(message):
    print("INPUT_SCENARIO|START|malformed_data")
    app = App(
        message_api=MalformedApi(),
        storage=ScenarioStorage(message),
    )
    app.state_manager.start(LoadingMainMenuState(app))
    app.state_manager.update()
    require_state(app, MainMenuCycleState, "malformed_data_fallback")


def runtime_recovery_scenario(app, message):
    print("INPUT_SCENARIO|START|runtime_recovery")
    start_home(app, message)
    app.state_manager.push_state(BrokenState())
    app.button = ScenarioInput(True, BUTTON_PRESS)
    app.dial = ScenarioInput(None, DIAL_EVENT)
    try:
        run_iteration(app)
    except Exception as error:
        recover_runtime_error(app, error)
    require_state(app, ErrorState, "runtime_recovery")


def run():
    print("INPUT_SCENARIOS_START")
    message = {
        "id": "scenario-1",
        "sender": "ella",
        "text": "Saved message text for scrolling and input testing " * 20,
        "utc": "2026-09-10T12:00:00Z",
    }
    app = App(
        message_api=ScenarioApi(),
        storage=ScenarioStorage(message),
    )
    messages_scenario(app, message)
    empty_messages_scenario(app, message)
    presets_scenario(app, message)
    settings_scenario(app, message)
    wifi_list_scenario(app, message)
    malformed_data_scenario(message)
    runtime_recovery_scenario(app, message)
    print("INPUT_SCENARIOS_COMPLETE")


if __name__ == "__main__":
    run()
