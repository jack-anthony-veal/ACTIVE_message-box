from micropython import const
from libraries.config import Config


SERVER_URL = None
TOKEN = None

SEND_JACK_URL = "http://projectserver.org/send/jack"
SEND_ELLA_URL = "http://projectserver.org/send/ella"
READ_JACK_URL = "http://projectserver.org/read/jack"
READ_ELLA_URL = "http://projectserver.org/read/ella"
PRESETS_JACK_URL = "http://projectserver.org/presets/jack"
PRESETS_ELLA_URL = "http://projectserver.org/presets/ella"


try:
    conf = Config.read('./config/network.ini')
except OSError:
    conf = {'login': {'ssid': '', 'pass': ''}}
WIFI_SSID: str = conf['login']['ssid']
WIFI_PASSWORD: str = conf['login']['pass']

PRESET_FILE: str = "./database/preset.txt"
NO_PRESETS_RESP: str = "No presets Upload on site"
IF_MESSAGE_NONE_DISP: str = "No new or saved messages!"

# INPUT DEVICES
LEFT_DIAL = const(-1)
RIGHT_DIAL = const(1)
DIAL_EVENT = const(4)
BUTTON_PRESS = const(3)

CHECK_MESSAGES_EVERY_MS: int = const(1500)
CHECK_PRESETS_EVERY_MS: int = const(15000)


MENU_OPTION = const(0)
PRESETS_OPTION = const(1)
SETTINGS_OPTION = const(2)



MENU_BACK_BUTTON: str = "Back"
PRESET_SEND_BUTTON: str = "Send"



LOOP_SLEEP_MS: int = const(20)
INPUT_DEBOUNCE_MS: int = const(150)

DISPLAY_FILE: str = const("./database/display.txt")

# BOOTING

ERROR_CODES = {
    "0": "unknown",
    "10": "HTTP",
    "11": "HTTP POST",
    "12": "HTTP GET",
    "13": "HTTP Json Invalid",
    "20": "DEVICE ERR",
    "21": "Display Error",
    "22": "Read Storage Error",
    "23": "Write Storage Error",
    "24": "Input Error",
    "30": "Software Error",
    "31": "Math Error",
    "32": "Parsing Error",
    "40": "No WIFI",
}
