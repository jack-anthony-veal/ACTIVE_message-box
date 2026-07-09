import app
from config import MENU_OPTIONS, MENU_OPTS_INDEX, MENU_Y
import time

from storage import Storage
from typing import *


# TODO: configure import
# TODO: configure type hints


# Grabs index
# Checks if index has just changed and refreshes if so
# If not, checks if the data to display can be refreshed
# If cant be refreshed it remains until input
# If it can it refreshes
# Upon a button press, it switches state
#


class MainMenuCycleState:
    def __init__(self, app):
        self.app = app # App Object

        self.options: list = MENU_OPTIONS # Config CONSTS

        self.current_index: int = 0 # Navigation index

        self.now_ms: Any = time.ticks_ms()

        # 0: msg, 1: preset, 2 none
        # TODO: make parse through the config list
        self.last_checks: list[Tuple[int, Any]] = [MENU_OPTS_INDEX[0][0], time.ticks_ms(),(MENU_OPTIONS[1][0], time.ticks_ms())]

        self.index_updated: bool = False # Checks if menu updated so a refresh can occur w/o overloading the disp
        self.input_event: Union[bool, None, int] = None #
        self.to_refresh:bool = False

        self.data_to_draw: Union[None, str] = None


    def enter_state(self) -> None: # Upon entering the state
        # attempts to load messages and display
        self.app.display.power_on()
        data: Any = None
        try:
            data: Union[list, str] = self.message_data()

        except Exception as api_message_ERR:  # TODO: Add a custom handler
            data = f'ERROR: {api_message_ERR}\nLikely no internet connection\n'

        finally:
            data_to_display = data if data is not None else "error entering main menu cycle state"
            self.app.display.custom_message(data_to_display, y_axis=8, wrap=True, fill_all=True)
            self.show_menu_bar()

        return

    # SHOWN CONSECUTIVE
    # input event only called if not none then return
    #
    #

    def handle_input_event(self, input_event: Union[bool, int, None], type_of_event) -> None:
        if self.input_event is None: return  # Reject none states
        if type_of_event == 'button':
            return # TODO : configure to switch states here

        self.load_new_selection() # Load screen display # TODO: maybe add to draw and then reload new screen on update?
        self.move_selection(self.input_event) # Shift the new index

        self.index_updated = True # Notify update state that the index has changed via input

        return



    def update_state(self):
        if self.index_updated: # checks if input occurred

            if self.current_index == 0:
                _, self.data_to_draw = self.message_data()

            elif self.current_index == 1:
                _, self.data_to_draw = self.preset_data()

            else:
                self.data_to_draw = self.settings_data()

            self.index_updated = False # reset
            self.to_refresh = False # reset
            return

        # if nor
        if self.current_index in [0, 1]: # Checks if data should display on refresh
            last_check_ms = self.last_checks[self.current_index][1]
            check_limit_ms = self.last_checks[self.current_index][1]

            # Valid refresh
            if self.refresh_clock(check_limit_ms, last_check_ms): # If should refresh init all reliant vars
                last_check_ms = time.ticks_ms()
                self.last_checks[self.current_index][1] = last_check_ms

                self.to_refresh = True # Data to draw

            else: # Invalid / Too fast of a refresh
                self.to_refresh = False # Wait until next update check called
                self.data_to_draw = None # No data to draw

            return

        self.data_to_draw = None

    def draw(self):
        if self.data_to_draw is not None:
            self.app.display.custom_message(self.data_to_draw, y_axis=8, wrap=True, fill_all=True)
            self.show_menu_bar()
            self.data_to_draw = None


        return

    def exit_state(self) -> None:
        self.current_index = self.current_index

        #
    # The functions below are specific to the state
    #
    # The ones above are of Base State
    #
    #
    #

    def show_menu_bar(self): # TODO: add consts used to self
        self.app.display.custom_message(self.options[self.current_index],
                                        x_axis=0, y_axis=MENU_Y,
                                        fill_start_line=MENU_Y, fill_x_axis=128, fill_y_axis=8
                                        )



    def move_selection(self, direction): # TRUE IS RIGHT, FALSE IS LEFT
        index_direction = 1 if direction else -1 # Added to remove redundancy
        updated_index = (self.current_index + index_direction) % len(MENU_OPTIONS) # returns the next available index
        self.current_index = updated_index # index changed
        self.index_updated = True


    def load_new_selection(self) -> Any: # displays_new_selection
        self.app.display.custom_message("Loading new selection...", fill_all=True) # TODO: Create loading opt in display dev


    def refresh_clock(self, ms_new_event_limit, last_check_ms):
    # TODO: add a storage and api cross check to prevent over refreshes
        refresh_value = True if time.ticks_diff(self.now_ms, last_check_ms) >= ms_new_event_limit else False
        return refresh_value # Returns true if last check > than refresh rate


    # Returns true if new data
    # TODO: configure with a const of data opts (dict)
    # def refresh_if_data_check(self):
    #     if self.current_index == 0:
    #         saved_data = self.app.storage.read_message_data()
    #         new_data_check, _ = self.message_data()
    #
    #     elif self.current_index == 1:
    #         saved_data = self.app.storage.read_preset_data()
    #         new_data_check, _ = self.preset_data()
    #
    #     if new_data_check:
    #         return False
    #
    #     else:
    #         return True



    def message_data(self): # always returns a last check time
        has_new_message, message_data = self.app.message_api.read_new_message()

        # No new message checks storage
        if not has_new_message: message_data = self.app.storage.read_display_data().get("message")
        if has_new_message: self.app.storage.write_display_data(message_data) # add to storage

        return has_new_message, message_data # Returns data



    def preset_data(self) : # TODO: Ensure api always uploads files fully with all presets so handler works (api.py)
        preset_data_available, preset_list = self.app.message_api.load_presets() # grab presets from api
        data = ['No new presets', 'available'] if not preset_data_available else preset_list # TODO: create a better handler this is very bug prone

        self.app.storage.write_preset_data(data) # add storage comparison

        return preset_data_available, data



    def settings_data(self): # TODO: create a setting state
        return "No settings page created yet..."


