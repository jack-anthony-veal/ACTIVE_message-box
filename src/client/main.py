import time

from app.app import App
from app.runtime import confirm_healthy, startup
from config.config import (
    DEVICE_OWNER, MAIN_LOOP_DRAW_DELAY_MS, MAIN_LOOP_UPDATE_DELAY_MS,
)


def main():
    startup_result = startup()
    if startup_result is None:
        print("STARTUP|BLOCKED")
        return
    updater, api = startup_result
    app = App(message_api=api, updater=updater)

    state_manager = app.state_manager
    state_manager.start(app.reset_state)
    state_manager.update()
    confirm_healthy(updater)
    print("STARTUP|HOME_READY")

    try:
        updater.flush_result(api, DEVICE_OWNER)
    except Exception as error:
        print("WARNING|update_result|{}".format(error))
    try:
        updater.check_and_install(api)
    except Exception as error:
        print("WARNING|update_check|{}".format(error))

    while True:
        button_event = app.button.event()
        if button_event is not None:
            state_manager.handle_input(button_event, app.button.event_type)
        dial_event = app.dial.event()
        if dial_event is not None:
            state_manager.handle_input(dial_event, app.dial.event_type)
        state_manager.update()
        time.sleep_ms(MAIN_LOOP_UPDATE_DELAY_MS)
        state_manager.draw()
        time.sleep_ms(MAIN_LOOP_DRAW_DELAY_MS)


if __name__ == "__main__":
    main()
