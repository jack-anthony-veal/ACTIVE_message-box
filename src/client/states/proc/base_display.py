# BaseMenu - > Init with list of opts and app.display
# MUST perform setup()
# then refresh_menu(INDEX) for refresh nav
# exit() for proper cleanup



class _Type:
    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self



Union = _Type() # Temp typing lib for locsal
Tuple = _Type()
Dict = _Type()
List = _Type()
import ujson
from micropython import const
import ubinascii as base64
import math
import gc
"tbf i did say this typinf class would be temporaru but icba to reimport so fuck it we ball "

"""
Universal lightweight class to draw the display screen

seperate instances for each menu

rather than inheriting app fully just the oled is needed as the class must be lightweight to have several instances

This also allows for each object to store the menu options for said state

"""

# BYTE_ARRAY SEPERATOR
_SEPERATOR = '~'

_ODD_FLAG = 1 << 0
_EVEN_FLAG = 1 << 1

# X AXIS MENU
_MENU_START_X = const(2)
_MENU_END_X = const(122)
_MENU_SIZE_X = const(120)

#Y AXIS MENU
_MENU_START_Y = const(53)
_MENU_END_Y = const(63)
_MENU_SIZE_Y = const(10)
_MAX_MENU_OPTS = const(3) # converted as a list
_MAX_CHARS_LINE = const(16)
_PX_PER_CHAR = const(8)

def _list_encoder(list_: Union[list, tuple], buffer: bytearray):
    length_ = len(list_)
    buffer = (bytes(_SEPERATOR.join(list_), 'utf-8')) # add to bytearray (sep with ,)
    return buffer

def _list_decoder(buffer: bytearray) -> tuple:
    opts_mv = memoryview(buffer) # Access a view of the buffer + return a tuple w/out copying
    opts_str = bytes(opts_mv).decode('utf-8') # decode data
    options_tup: tuple = tuple(map(lambda x: x, opts_str.split(_SEPERATOR))) # convert into fixed tuple
    return options_tup

def _dict_encoder(dict_: dict, buffer: bytearray) -> bytes:
    dict_=str(dict_); dict_=dict_.encode('ascii');
    encoded = base64.b2a_base64(dict_)
    buffer = bytes(encoded)
    return encoded
    
def _dict_decoder(buffer: bytearray) -> dict:
    dict_bytes = base64.a2b_base64(
        bytes(
            memoryview(
                buffer
                )
            )).decode('utf-8') # decodes base 64 memory view of dict
    
    try:
        dict_output = eval(dict_bytes)
        if type(test_obj) != list:
            raise ValueError("Trouble parsing with eval")
    except: # avoids using json loads as replacing brackets is dangerous
        dict_bytes = dict_bytes.replace("'", "\"")
        dict_output = ujson.loads(str(dict_bytes))
    
    return dict_output  


class BaseMenu:
    def __init__(self, display, opts: List[str]) -> None: # -> Takes state.app.display and list of menu opts
        self.oled = display.oled # display obj
        self.icons = display.draw_art
        # Handler for invalid inputs
        if (opts is None or len(opts) < 1): raise ValueError("No options for menu") # Handle no opts
        if (type(opts) is not list): raise TypeError("Not provided a list") # Handle type errors
        try: opts = [str(x) for x in opts]
        except: raise TypeError("Values in list cannot convert to str") # Handle unknown types
        if (len(''.join(opts)) > _MAX_CHARS_LINE): raise ValueError("Options lists index's are too large") # Handle > 16
        
        # inst var
        
        # Buffers
        self.menu_dict_buffer = bytearray(100)
        self.menu_options_buffer: Union[None, bytearray] = None # 16 bytes max on display (16 chars where 1 char = 1b) so assign ~20 for mem safety
        self.px_per_opt: Union[None, int] = None
        
        #--
        self.chars_per_opt: Union[None, int] = None
        self.option_selected: Union[int, None] = None
        self.raw_opts: list = opts
        self.options_length = len(opts)
        
    """ Utilities """
        
    def setup(self):
        self.oled.fill(0)
        self._init_vectors()
        self._read_opts()
        self._map_dimensions()
        self.refresh_menu()
        
        del self.raw_opts
        
    def reset(self, fill=False):
        if fill:
            self.oled.fill(0)
            
        self.menu_dict_buffer = b'\x00' * len(self.menu_dict_buffer)
        self.menu_options_buffer = b'\x00' * len(self.menu_options_buffer)
        del (
            self.oled, self.icons, self.px_per_opt,
            self.chars_per_opt, self.option_selected,
            self.raw_opts, self.options_length
            )
        gc.collect()
        
    
    """ Buffer Decode / Encoder"""
        
    
    
    @property
    def _read_opts(self) -> tuple: # Retrieves opts when needed and maps as a tuple
        menu_opts_mv = memoryview(self.menu_options_buffer) # Access a view of the buffer + return a tuple w/out copying
        menu_opts_str = bytes(menu_opts_mv).decode('utf-8') # decode data
        menu_options_tup: tuple = tuple(map(lambda x: x, menu_opts_str.split(_SEPERATOR))) # convert into fixed tuple
        return menu_options_tup
    
    # assign values to vectors on inst
    
    def _init_vectors(self) -> None:
        self.menu_options_buffer = bytearray(20) # init buffer
        
        self.px_per_opt: int = math.floor(_MENU_SIZE_X / ((self.options_length))) # calc px per box param
        self.chars_per_opt: int = math.floor(self.px_per_opt) // (self.options_length) + 1 #  calculate chars per box params
        
        opts = [option_[:self.chars_per_opt] for option_ in self.raw_opts] # splice to fit option box params
        
        self.menu_options_buffer = (bytes(_SEPERATOR.join(opts), 'utf-8')) # add to bytearray (sep with ,)

    # Maps dimensions for objs
    def _map_dimensions(self) -> None:
        """ Vars and general inst calcs"""
        
        options: tuple = self._read_opts
        
        options_length: int = self.options_length
        if options_length == 0: raise ValueError("Cant // by 0")

        options_px_space_int: int = self.px_per_opt
        
        total_menu_space_x = _MENU_SIZE_X
        
        start_x = _MENU_START_X
        end_x = _MENU_END_X
        start_y = _MENU_START_Y
        flag_divisible = 0        
        vectors: dict = {} # Key (Index) : Value (Tuple(X, Y)
        
        " ensuring list is even so that merge sort doesnt doubly assign "
        final_index = math.floor((options_length) / 2)
 
        if ((options_length + 1) % 2 == 0):
            flag_divisible |= _ODD_FLAG
        else:
            flag_divisible |= _EVEN_FLAG  # Determine odd or even 
        
        if (_ODD_FLAG & flag_divisible):
            vectors[options_length//2] = tuple((int(options_length//2 * options_px_space_int), start_y)) # Assign here to avoid double assign      
        
        
        " O (log(n)) mapping dimensions binary sort"
        for counter in range(1, final_index+1):
            pixel_offset = lambda direction: (direction) * options_px_space_int

            foward_x: int = pixel_offset((counter-1)) + 1
            backward_x: int = pixel_offset((options_length-1)-(counter-1)) + 1
            
            vectors[str((counter-1))]: Dict[str, Union[Tuple[Union[int, str]], None]] = [foward_x, start_y]
            vectors[str(((options_length-1)-(counter-1)))]: Dict[str, Union[Tuple[Union[int, str]], None]] = [backward_x, start_y]
    
        self.menu_dict_buffer = _dict_encoder(vectors)
    
    """ Refreshes the menu with provided options"""
    
    def refresh_menu(self, index=None, icons=False) -> None:
        # Handler
        if type(index) is not int and index is not None: raise TypeError("not int or none")
        
        
        options = list(self._read_opts)
        vectors = _dict_decoder(self.menu_dict_buffer)

        # allow for icons
        if not icons:
            oled = self.oled
        else:
            oled = self.icons

        for increment_ in range(0, 10, 2): oled.vline(1, 53+increment_,2, 1); oled.vline(122, 53+increment_,2,1) # borders
        
        
        # if integer indez (selected)
        if type(index) is int:
            if (index > self.options_length): raise IndexError("larger than opts")
            sel_x = (vectors[str(index)][0])
            sel_y = (vectors[str(index)])[1]

            # grab the vector cords
            oled.fill_rect(sel_x, sel_y+1, self.px_per_opt, 9, 1) # fill
            oled.text(str(options[index]), sel_x + 1, sel_y+2, 0) # addcolorless text w slight offset
        
        for point_ in range(1, 124, 4):
            oled.hline(point_, 53, 2, 1) # borders
            oled.hline(point_, 63, 2, 1)
        
        """
Big ol' fuckery mc mfuckerson down here dont ever touch this stupid function ever again 
"""
        # non selected vals
        if len(vectors.values()) > 1: #fuckpython this stupid fucking language wdym i cant fucking unpack a tuple w vals < 2 do one u stupid cunt
            for x in options:
                for increment_ in range(0, 10, 2): oled.vline(x, y+increment_, 1,1) # seperators

            for key, vals in vectors.items(): # add text
                if int(key) == index: continue
                x = vals[0]
                y = vals[1]
                
                text_=options[int(key)]
                oled.fill_rect(x, y+1, self.px_per_opt, 9, 0)                
                oled.text(text_, x+1, y+2, 1)
            
        oled.show()

        


class BaseScroll:
    def __init__(self, oled, options: Union[list, tuple]):
        self.oled = oled
        self.options = options
        self.length = len(options)
        self.y_max = _MENU_START_Y-1
        self.y_min = 1
        self.y = self.y_max - self.y_min
        self.x = 120
        self.x_max = 122
        self.x_min = 2
        self.max_toShow = 2 # starting w 0
        
        """ buffers """
        self.options_buf = bytearray(200)
        
        self.display_locs = (
            (1, 1),
            (1, 19),
            (1, 37),
        )
    def setup(self):
        self._init_vectors()
        self.scroll()
        
    
    def _init_vectors(self):
        opts = self.options
        max_charsPerOpt = math.floor(self.x / 8)
        opts = [opts[:max_charsPerOpt] for option in opts]
        self.options_buf = _list_encoder(opts, self.options_buf)
        
    def scroll(self, index_=0):
        if index_ > self.length: return
        data = _list_decoder(self.options_buf)
        wrap_index = lambda x: (x + index_) % self.length_
        second = wrap_index(+1); third = wrap_index(+1)
        text = [index_, second, third]
        
        for index, location in enumerate(self.display_locs):
            self.oled.fill_rect(location[0], location[1], self.x_max, self.y_max-1, 0)
            self.oled.hline(location[0], location[1], self.x_max, 1)
            self.oled.hline(location[0], location[1] + 18, self.x_max, 1)
            self.oled.vline(location[0], location[1], 18, 1)
            self.oled.vline(location[0]+self.x_max, location[1], 18, 1)
            
            if index != 0:
                self.oled.text(data[test[index]], location[0] + 1, location[1] + 1, 1)
            else:
                self.oled.fill_rect(location[0], location[1], self.x_max, self.y_max, 1)
                self.oled.text(data[test[index]], location[0] + 1, location[1] + 1, 0)
                
                
        self.oled.show()

      