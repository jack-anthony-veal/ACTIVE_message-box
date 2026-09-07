from app.StateNavigator import StateNavigator
from app.api import MessageApiClient
from hardware_devices.display_device import Display
from hardware_devices.input_device import Button, Dial
from hardware_devices.storage import Storage
from states.home.LoadingMainMenuState import LoadingMainMenuState
from app.updater import UpdateManager


class App:
    def __init__(
        self, message_api=None, display=None, storage=None,
        dial=None, button=None, updater=None,
    ):
        self.message_api = message_api or MessageApiClient()
        self.display = display or Display()
        self.storage = storage or Storage()
        self.dial = dial or Dial()
        self.button = button or Button()
        self.updater = updater or UpdateManager()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.flags = 0
