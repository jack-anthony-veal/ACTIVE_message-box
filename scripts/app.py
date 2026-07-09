import input_device
from display_device import *
from input_device import *
from menu_handler import *
from storage import *
from debug import Debug
from api import *


d = Debug(debug=True)
printd = d.DEBUG_PRINTLN

# Boot the box
class App:
    def __init__(self):
        self.message_api: MessageApiClient = MessageApiClient(server_url=SERVER_URL, api_token=TOKEN)
        self.display: OledDisplay = OledDisplay()
        self.menu = MenuHandler()
        self.storage = Storage()
        self.last_message_check_ms = time.ticks_ms()
        self.status_codes = {}
        self.input_device = ToggleInput()
