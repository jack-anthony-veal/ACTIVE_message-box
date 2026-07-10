from app.app import App
from app.StateNavigator import StateNavigator
from states.MainMenuState import MainMenuCycleState
from states.PresetMenu import PresetMenu
from config.config import *
import time
import os

print(os.listdir("./"))

# TODO: create files if none on boot


def main():
    app = App() # declare object superclass
    state_manager = StateNavigator(app) # Inst state nav


    state_manager.push_state(MainMenuCycleState(app))

    while state_manager.current_state_check is None: # Ensure that state manager doesn't call upon empty objects
        time.sleep_ms(10)

    input_event_switch = None

    while True: # TODO: configuren a button device read
        input_event_type = ''
        input_event_button = app.input_device.button() # Input
        input_event_switch = app.input_device.switch() # Input

        if input_event_button is not None:
          input_event_type = 'button'
          state_manager.handle_input(event=input_event_button, event_type=input_event_type)


        if input_event_switch is not None:
            input_event_type = 'switch'
            state_manager.handle_input(event=input_event_switch, event_type=input_event_type)

        time.sleep_ms(30)
        state_manager.update()
        state_manager.draw()



if __name__ == '__main__':
    main()