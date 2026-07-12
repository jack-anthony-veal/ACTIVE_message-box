import time

import gc

from libraries.utils import message_from_payload
from libraries.utils.ascii import *
import math

def add_text_to_box(title, data, screen):
    data: str = str(data)[:13] if len(data) > 13 else str(data)
    title: str = str(title)[:13] if len(title) > 13 else str(title)
    new_: list = []
    for line, text in enumerate([title, data]):
        left_space_t: int = math.floor((14 - len(text)) / 2)
        right_space_t: int = math.ceil((14 - len(text)) / 2)
        text_final: str = str(left_space_t * ' ') + str(text) + str(right_space_t * ' ')
        if line == 0:
            title: str = text_final
        if line == 1:
            data:str = text_final

    for line_, text_ in enumerate(screen):
        if line_ == 1:
            new_.append([str('|' + title + '|')])
        elif line_ == 4:
            new_.append([str('|' + data + '|')])
        else:
            new_.append(text_)

    return list(new_)




class Notify:
    def __init__(self, app, data, title):
        try:
            try:
                title = str(title)
                data = str(data)

            except:
                title = repr(title)
                data = repr(data)
        except:
            title = "Unknown Error"
            data = "Please Restart"


        self.app = app
        self.data: str = data
        self.screen = CUTE_NOTIFY_ERROR_BOX
        self.displayed = False
        self.title: str = title

    def enter_state(self):
        self.draw()

    def update(self):
        return

    def draw(self):
        if self.displayed: return

        self.app.display.custom_message()

        data: list = add_text_to_box(self.title, self.data, self.screen)

        self.app.display.custom_message(data, fill_all=True, x_axis=0, y_axis=0, wrap=True)
        self.displayed = True

    def handle_input(self, event, type):
        if type == 'button' and event is not None:
            self.app.state_manager.reset()

    def exit_state(self):
        return



class ErrorState:
    def __init__(self, app, data, error_code=0, fatal=False, last_state=None):
        self.app = app
        self.data = data
        self.screen_http = CUTE_API_ERROR_BOX
        self.screen_minor = CUTE_ERROR_BOX
        self.screen_wifi = CUTE_WIFI_ERROR_BOX
        self.displayed = False
        self.screen = self.screen_minor
        self.fatal = fatal
        self.last_state = app.reset_state if last_state is None else last_state

        self.error_codes = {
            0: "unknown",
            10: "HTTP",
            11: "HTTP POST",
            12: "HTTP GET",
            13: "HTTP Json Invalid",
            20: "DEVICE ERR",
            21: "Display Error",
            22: "Read Storage Error",
            23: "Write Storage Error",
            24: "Input Error",
            30: "Software Error",
            31: "Math Error",
            32: "Parsing Error"
        }
        self.call_time = time.ticks_ms()

    def enter_state(self):
        self.draw()

    def update(self):
        if not self.fatal:
            if time.ticks_diff(time.ticks_ms(), self.call_time) > 10000:
                self.app.state_manager.replace_state(self.last_state)

    def draw(self):
        if not self.displayed:
            self.app.display.custom_message()
            self.app.display.custom_message(self.screen, fill_all=True, x_axis=0, y_axis=0, wrap=True)
            self.displayed = True

    def handle_input(self, event, type):
        if type == 'button' and event is not None:
            if self.fatal:
                try:
                    gc.collect()
                    self.app.state_manager.reset()

                except Exception as err:
                    print(err) # TODO: log on txt
                    from machine import Pin, deepsleep, reset

                    try:
                        # TODO: Make screen nicer
                        self.app.display.custom_message("Fatal Error... Resetting \n :'(", fill_all=True)
                        time.sleep(5)

                    except Exception as errFatal:
                        print(errFatal)

                    reset()
            else:
                self.app.state_manager.replace_state(self.last_state)

    def exit_state(self):
        return
