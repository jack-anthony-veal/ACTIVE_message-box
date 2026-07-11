import os
import time
from hardware_devices.input_device import *
from app.app import App
from hardware_devices.input_device import Dial
from states.LoadingMainMenuState import LoadingMainMenuState

print(os.listdir("./"))

# TODO: create files if none on boot


def main():
    app = App() # declare object superclass
    state_manager = app.state_manager # Inst state nav
    state_manager.start(LoadingMainMenuState(app))


    while state_manager.current_state_check is None: # Ensure that state manager doesn't call upon empty objects
        time.sleep_ms(10)

    input_event_switch = None

    button = app.button  # Input
    dial = app.dial
    while True: # TODO: configuren a button device read
    # Input

        button_event = button.event()
        if button_event is not None:
            state_manager.handle_input(event=button_event, event_type=button.event_type)

        dial_event = dial.event()
        if dial_event is not None:
            state_manager.handle_input(event=dial_event, event_type=dial.event_type)

        time.sleep_ms(30)
        state_manager.update()
        state_manager.draw()



if __name__ == '__main__':
    main()
