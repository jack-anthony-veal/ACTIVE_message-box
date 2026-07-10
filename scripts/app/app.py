from hardware_devices.display_device import *
from hardware_devices.input_device import *
from hardware_devices.storage import *
from libraries.utils.debug import Debug
from app.api import MessageApiClient
from config.config import *
from app.StateNavigator import StateNavigator
from app import PresetMenu
from app import MainMenuCycleState

d = Debug(debug=True)
printd = d.DEBUG_PRINTLN

# Boot the box
class App:
    def __init__(self):
        self.message_api: MessageApiClient = MessageApiClient()
        self.display: OledDisplay = OledDisplay()
        self.storage = Storage()
        self.status_codes = {}
        self.input_device = ToggleInput()
        self.PresetMenu = PresetMenu(self)
        self.MainMenuCycleState = MainMenuCycleState(self)
        self.state_manager = StateNavigator(self)
