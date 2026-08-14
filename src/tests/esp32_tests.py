import gc
import network
import time
from machine import I2C, Pin

from app.api import MessageApiClient
from hardware_devices.display_device import OledDisplay
from hardware_devices.input_device import Button, Dial
from hardware_devices.storage import Storage


RESULTS = []


def check(name, function):
    try:
        detail = function()
        RESULTS.append(("PASS", name, "" if detail is None else str(detail)))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


def check_wifi():
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        raise RuntimeError("Wi-Fi is disconnected")
    return "connected"


def check_i2c():
    bus = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
    devices = bus.scan()
    if 0x3C not in devices:
        raise RuntimeError("OLED address 0x3C missing: " + str(devices))
    return devices


def check_display():
    display = OledDisplay()
    display.power_on()
    display.custom_message("Diagnostics OK", fill_all=True, x_axis=0, y_axis=8, wrap=True)
    time.sleep_ms(250)
    return "draw completed"


def check_storage_restore():
    paths = ("./database/display.txt", "./database/preset.txt")
    originals = []
    for path in paths:
        file = open(path, "r")
        originals.append(file.read())
        file.close()

    try:
        storage = Storage()
        storage.write_display_data("diagnostic-message")
        if storage.read_display_data().get("message") != "diagnostic-message":
            raise RuntimeError("display storage mismatch")
        storage.write_preset_data(["diagnostic-preset"])
        if storage.read_preset_data().get("presets") != ["diagnostic-preset"]:
            raise RuntimeError("preset storage mismatch")
    finally:
        for index, path in enumerate(paths):
            file = open(path, "w")
            file.write(originals[index])
            file.close()
    return "round trip restored"


def check_inputs():
    dial = Dial()
    button = Button()
    return "dial=" + str(dial.rotary_encoder.value()) + " button=" + str(button.button_pin.value())


def check_message_read():
    success, data = MessageApiClient().read_new_message()
    return "success=" + str(success) + " type=" + type(data).__name__


def check_preset_read():
    success, presets = MessageApiClient().load_presets()
    if not success or not presets:
        raise RuntimeError("no presets returned")
    return "count=" + str(len(presets))


def check_real_send():
    result = MessageApiClient().send_preset("[message-box diagnostic test]")
    if type(result) != tuple or len(result) != 2:
        raise RuntimeError("send returned " + repr(result))
    if not result[0]:
        raise RuntimeError("send failed: " + repr(result[1]))
    return "HTTP send accepted"


check("Wi-Fi connected", check_wifi)
check("OLED present on I2C", check_i2c)
check("OLED draw", check_display)
check("Storage write/read/restore", check_storage_restore)
check("Input hardware construction", check_inputs)
check("Message endpoint", check_message_read)
check("Preset endpoint", check_preset_read)
check("Real send endpoint", check_real_send)
gc.collect()
RESULTS.append(("INFO", "Free heap", str(gc.mem_free())))

for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

print("DEVICE_TESTS_COMPLETE")
