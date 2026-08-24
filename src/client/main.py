import time

from app.app import App
from config.config import MAIN_LOOP_DRAW_DELAY_MS, MAIN_LOOP_UPDATE_DELAY_MS


def main():
    app = App()
    state_manager = app.state_manager
    state_manager.start(app.reset_state)

    button = app.button
    dial = app.dial
    while True:
        button_event = button.event()
        if button_event is not None:
            state_manager.handle_input(
                event=button_event,
                event_type=button.event_type,
            )

        dial_event = dial.event()
        if dial_event is not None:
            state_manager.handle_input(
                event=dial_event,
                event_type=dial.event_type,
            )

        state_manager.update()
        time.sleep_ms(MAIN_LOOP_UPDATE_DELAY_MS)
        state_manager.draw()
        time.sleep_ms(MAIN_LOOP_DRAW_DELAY_MS)


if __name__ == "__main__":
    main()
