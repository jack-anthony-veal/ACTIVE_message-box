import time
import gc
import network
from config.config import *

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
        self.app.display.show_error("state_success", title_text, body_text)
        self.displayed = True

    def handle_input(self, event, type):
        if type == BUTTON_PRESS and event is not None:
            self.app.state_manager.reset()

    def exit_state(self):
        return



class ErrorState:
    def __init__(self, app, data="", error_code=0, fatal=False, last_state=None):
        self.app = app
        self.data = str(data)
        self.displayed = False
        self.fatal = fatal
        self.safe_state = self.app.safe_state
        self.last_state = app.reset_state if last_state is None else last_state
        self.error_code = error_code
        self.error_codes = ERROR_CODES


    def enter_state(self):
        connected_ = network.WLAN(network.STA_IF).isconnected()

        if not connected_:
            self.screen = "state_wifi_error"
            self.error_code = 40
            self.draw()
            del connected_
            return

        code = self.error_code

        if code == 0:
            screen = "state_generic_error"
        elif code in range(10,14):
            screen = "state_http_error"
        elif code in range(20, 25):
            screen = "state_device_error"
        elif code in range(30, 33):
            screen = "state_software_error"
        elif code == 40:
            screen = "state_wifi_error"
        else:
            screen = "state_generic_error"

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
                    from machine import Pin, deepsleep, reset

                    try:
                        # TODO: Make screen nicer
                        self.app.display.begin_screen("Fatal error")
                        self.app.display.draw_text_block(
                            "Resetting the device", 12, 88, 216
                        )
                        time.sleep(5)

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
