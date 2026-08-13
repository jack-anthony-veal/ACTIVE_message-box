from states.proc.StateNavigator import StateNavigator
from app.api import MessageApiClient
from config import config
from hardware_devices.display_device import *
from hardware_devices.input_device import *
from hardware_devices.storage import *
from libraries.utils.debug import Debug
from states.presets.LoadingPresetsState import LoadingPresetsState
from states.home.LoadingMainMenuState import LoadingMainMenuState
from states.home.MainMenuState import MainMenuCycleState

d = Debug(debug=True)
printd = d.DEBUG_PRINTLN

_OTHER = 1 << 0
_NON_FATAL_API = 1 << 1
_NON_FATAL_WIFI= 1 << 2
_NON_FATAL_HTTP= 1 << 3
_NON_FATAL = 1 << 4

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
