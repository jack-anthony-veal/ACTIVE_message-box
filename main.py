import time
from app.app import App
from states.LoadingMainMenuState import LoadingMainMenuState
from app.exception_handler import print_exception
from states.WIFI import WifiState

# TODO: create files if none on boot


def main():
    # app = App() # declare object superclass
    # state_manager = app.state_manager # Inst state nav
    #

    app = App() # declare object superclass
    state_manager = app.state_manager # Inst state nav
    state_manager.start(LoadingMainMenuState(app))

    while state_manager.current_state_check is None: # Ensure that state manager doesn't call upon empty objects
        time.sleep_ms(3)


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

        state_manager.update()
        time.sleep_ms(2)
        state_manager.draw()
        time.sleep_ms(2)
        
    




if __name__ == '__main__':

    main()

