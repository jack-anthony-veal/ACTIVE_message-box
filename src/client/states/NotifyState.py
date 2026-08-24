import time
import gc
import network

from assets.registry import ICONS
from config.config import (
    BUTTON_PRESS, CONTENT_TOP, ERROR_CODES, ERROR_DEVICE_MAX_EXCLUSIVE,
    ERROR_DEVICE_MIN, ERROR_HTTP_MAX_EXCLUSIVE, ERROR_HTTP_MIN,
    ERROR_SOFTWARE_MAX_EXCLUSIVE, ERROR_SOFTWARE_MIN, ERROR_UNKNOWN,
    ERROR_WIFI, FATAL_ERROR_DISPLAY_MS, SCREEN_MARGIN, SCREEN_WIDTH,
    STATE_TEXT_FALLBACK_OFFSET_Y,
)

def add_text_to_box(title, data):
    return str(title), str(data)

class Notify:
    def __init__(self, app, data, title):
        try:
            title = str(title)
            data = str(data)
        except Exception:
            title = "Unknown Error"
            data = "Please Restart"


        self.app = app
        self.data: str = data
        self.screen = None
        self.displayed = False
        self.title: str = title

    def enter_state(self):
        self.draw()

    def update(self):
        return

    def draw(self):
        if self.displayed: return
        title_text, body_text = add_text_to_box(self.title, self.data)
        self.app.display.show_error(
            ICONS["state"]["success"], title_text, body_text
        )
        self.displayed = True

    def handle_input(self, event, type):
        if type == BUTTON_PRESS and event is not None:
            self.app.state_manager.reset()

    def exit_state(self):
        return



class ErrorState:
    def __init__(
        self, app, data="", error_code=ERROR_UNKNOWN,
        fatal=False, last_state=None,
    ):
        self.app = app
        self.data = str(data)
        self.displayed = False
        self.fatal = fatal
        self.last_state = app.reset_state if last_state is None else last_state
        self.error_code = error_code
        self.error_codes = ERROR_CODES


    def enter_state(self):
        connected_ = network.WLAN(network.STA_IF).isconnected()

        if not connected_:
            self.screen = ICONS["state"]["wifi_error"]
            self.error_code = ERROR_WIFI
            self.draw()
            del connected_
            return

        code = self.error_code

        if code == ERROR_UNKNOWN:
            screen = ICONS["state"]["generic_error"]
        elif code in range(ERROR_HTTP_MIN, ERROR_HTTP_MAX_EXCLUSIVE):
            screen = ICONS["state"]["http_error"]
        elif code in range(ERROR_DEVICE_MIN, ERROR_DEVICE_MAX_EXCLUSIVE):
            screen = ICONS["state"]["device_error"]
        elif code in range(ERROR_SOFTWARE_MIN, ERROR_SOFTWARE_MAX_EXCLUSIVE):
            screen = ICONS["state"]["software_error"]
        elif code == ERROR_WIFI:
            screen = ICONS["state"]["wifi_error"]
        else:
            screen = ICONS["state"]["generic_error"]

        self.screen = screen

        del code, connected_
        self.draw()

    def update(self):
        pass

    def draw(self):
        if self.displayed: return

        codes = dict(self.error_codes)
        data = self.data
        try:
            spec_code = codes[str(self.error_code)]
            title_ = f'M-B:{str(self.error_code)} {spec_code}'
       
        except Exception:
            title_ = "whoops... an error occurred"

        body_ = data if data is not None else "sorry :( press back pls"


        title_text, body_text = add_text_to_box(title=title_, data=body_)
        self.displayed = True

        self.app.display.show_error(self.screen, title_text, body_text)

    def handle_input(self, event, type):
        if type is None and event is None: return

        if type == BUTTON_PRESS:
            if self.fatal:
                try:
                    gc.collect()
                    self.app.state_manager.reset()

                except Exception:
                    from machine import reset

                    try:
                        # TODO: Make screen nicer
                        self.app.display.begin_screen("Fatal error")
                        self.app.display.draw_text_block(
                            "Resetting the device",
                            SCREEN_MARGIN,
                            CONTENT_TOP + STATE_TEXT_FALLBACK_OFFSET_Y,
                            SCREEN_WIDTH - SCREEN_MARGIN * 2,
                        )
                        time.sleep_ms(FATAL_ERROR_DISPLAY_MS)

                    except Exception:
                        reset()
                        return
            else:
                state = self.last_state
                if state is self.app.reset_state:
                    state = state.__class__(self.app)

                gc.collect()
                self.app.state_manager.replace_state(state)
                return

    def exit_state(self):
        return
