_DIRTY = 1 << 0

from states.proc.base_display import BaseMenu, BaseScroll
from config.config import DIAL_EVENT, BUTTON_PRESS as BUTTON_EVENT

class SettingsNav:
    def __init__(self, app):
        self.app = app
        self.index_flag = 0 # shifts if main screen moves
        self.settings_flag = 1
        self.menu_flag = 0 # becomes menu dirty if pressed
        self.current_index = 0
        
        self.settings_menu = ["account", "device", "wifi", "graphics", "tbd"]
        self.options_menu = ["edit", "back"]
        
        self.menu_size = len(self.options_menu)
        self.settings_size = len(self.settings_menu)
        
        self.MENU_CONTROLLER = BaseMenu(self.app.display, self.options_menu)
        self.SETTINGS_CONTROLLER = BaseScroll(self.app.display.oled, self.settings_menu)
        
    def enter_state(self):
        self.MENU_CONTROLLER.setup()
        self.SETTINGS_CONTROLLER.setup()
        self.settings_flag=1
        self.menu_flag=0
        self.index_flag |= _DIRTY
        
    def exit_state(self):
        pass
    
    def handle_input(self, _event, _type):
        if _type == DIAL_EVENT:
            self.current_index = (self.current_index + event) % self.settings_menu
            self.index_flag |= _DIRTY
            self.draw()
            return
        
        if _type == BUTTON_EVENT and (self.settings_flag & _DIRTY):
            self.settings_flag = 0
            self.menu_flag |= _DIRTY
            self.current_index=0
            self.index_flag |= _DIRTY
            self.draw()
            return
        
        if _type == BUTTON_EVENT and (self.menu_flag & _DIRTY):
            if self.current_index == 1:
                self.current_index = 0
                self.menu_flag = 0
                self.settings_flag |= _DIRTY
                self.index_flag |= _DIRTY
                self.draw()
                return
            
    def draw(self):
        if not self.index_flag & _DIRTY: return
        if self.settings_flag & _DIRTY:
            self.SETTINGS_CONTROLLER.refresh(self.current_index)
            if self.current_index == 0:
                self.MENU_CONTROLLER.refresh(None)
                
        elif self.menu_flag & _DIRTY:
            self.MENU_CONTROLLER.refresh(self.current_index)
        self.index_flag = 0
            
    def update(self):
        return
    