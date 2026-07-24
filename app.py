from app.StateNavigator import StateNavigator
from app.api import MessageApiClient
from config import config
from hardware_devices.display_device import *
from hardware_devices.input_device import *
from hardware_devices.storage import *
from libraries.utils.debug import Debug
from states.LoadingPresetsState import LoadingPresetsState
from states.LoadingMainMenuState import LoadingMainMenuState
from states.MainMenuState import MainMenuCycleState

d = Debug(debug=True)
printd = d.DEBUG_PRINTLN

_HTTP_F = 1 << 0
_API_F = 1 << 1
_WIFI_F = 1 << 2

# Boot the box
class App:
    def __init__(self):
        self.message_api: MessageApiClient = MessageApiClient()
        self.display: OledDisplay = OledDisplay()
        self.storage = Storage()
        self.status_codes = {}
        self.dial = Dial()
        self.button = Button()
        self.preset_state = LoadingPresetsState(self)
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.safe_state = MainMenuCycleState(self, "error loading! try restarting!!")
        self.config = config
        self.flags = 0
