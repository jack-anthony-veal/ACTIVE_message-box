import input_device
from display_device import *
from input_device import *
from storage import *
from debug import Debug
from api import *
from config import *
from PresetMenu import *
from MainMenuState import *
from StateNavigator import *


d = Debug(debug=True)
printd = d.DEBUG_PRINTLN

# Boot the box
class App:
    def __init__(self):
        self.message_api: MessageApiClient = MessageApiClient(server_url=SERVER_URL, api_token=TOKEN)
        self.display: OledDisplay = OledDisplay()
        self.storage = Storage()
        self.status_codes = {}
        self.input_device = ToggleInput()
        self.PresetMenu = PresetMenu(self)
        self.MainMenuCycleState = MainMenuCycleState(self)
        self.state_manager = StateNavigator(self)
