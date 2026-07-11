from libraries.utils.ascii import *

class Notify:
    def __init__(self, app, data, title):
        self.app = app
        self.data = data[:13] if len(data) > 12 else data
        self.screen = CUTE_NOTIFY_ERROR_BOX
        self.text_index = cute_notify_text_vars
        self.displayed = False
        self.title = title[:13] if len(title) > 12 else title

    def enter_state(self):
        self.draw()

    def draw(self):
        if self.displayed: return

        self.app.display.custom_message()

        new_ = []
        for line, text in enumerate(self.screen):
            if line == 1:
                new_.append([str('|' + self.title + '|')])
            elif line == 4:
                new_.append([str('|' + self.data + '|')])
            else: new_.append(text)


        self.app.display.custom_message(new_, fill_all=True, x_axis=0, y_axis=0, wrap=False)
        self.displayed = True

    def handle_input(self, event, type):
        if type == 'button' and event is not None:
            self.exit_state()

    def exit_state(self):
        self.app.state_navigator.reset()

class HTTPError:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.screen = CUTE_API_ERROR_BOX
        self.displayed = False

    def enter_state(self):
        self.draw()

    def draw(self):
        if not self.displayed:
            self.app.display.custom_message()
            self.app.display.custom_message(self.screen, fill_all=True, x_axis=0, y_axis=0, wrap=False)
            self.displayed = True

    def handle_input(self, event, type):
        if type == 'button' and event is not None:
            self.exit_state()

    def exit_state(self):
        self.app.state_navigator.reset()
