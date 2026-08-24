from app.StateNavigator import StateNavigator
from app.api import MessageApiClient
from hardware_devices.display_device import Display
from hardware_devices.input_device import Button, Dial
from hardware_devices.storage import Storage
from states.home.LoadingMainMenuState import LoadingMainMenuState


class App:
    def __init__(self):
        self.message_api = MessageApiClient()
        self.display = Display()
        self.storage = Storage()
        self.dial = Dial()
        self.button = Button()
        self.state_manager = StateNavigator(self)
        self.reset_state = LoadingMainMenuState(self)
        self.flags = 0
