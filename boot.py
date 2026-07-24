import gc
import sys
import time
import esp
from machine import I2C
import network
import esp32
from machine import Pin, reset
from config.config import *
from libraries import sh1106
from libraries.rotary_irq_esp import RotaryIRQ
from start_up.tests import *
from hardware_devices.input_device import OnSwitch

switch = OnSwitch()
wake_pins = switch.wake_up_pins
del switch

# Trigger level: WAKEUP_ALL_LOW wakes up if ANY pin in the tuple drops to LOW
sys.path.append('config')
print(str(get_reset_reason()))
gc.collect()


try:
    i2c_bus = I2C(
        0,
        scl=Pin(I2C_SCL_PIN),
        sda=Pin(I2C_SDA_PIN),
        freq=100000
    )

    dial = RotaryIRQ(
                pin_num_clk=18,
                pin_num_dt=19,
                incr=1,
                range_mode=RotaryIRQ.RANGE_WRAP,
                pull_up = True,
                half_step=False,
                reverse=True,
    )

    button = Pin(
                23,
                Pin.IN,
                Pin.PULL_UP
    )

except Exception as FATALERR:
    print(str(FATALERR))
    time.sleep(3)
    gc.collect()
    reset()


def test_cycle(button_, dial_, i2c_):
    fetch_api_token()
    time.sleep_ms(50)
    repr(test_i2c_bus(i2c_, (I2C_HEX_1, I2C_HEX_2)))
    time.sleep_ms(50)
    repr(test_encoder_idle(dial_))
    time.sleep_ms(50)
    repr(test_button_idle(button_))
    time.sleep_ms(50)
    repr(test_free_storage())
    time.sleep_ms(20)
    repr(test_storage())
    time.sleep_ms(20)



def wifi_stats():
    station = network.WLAN(network.STA_IF)
    if station.isconnected():
        return True
    else: return False


def connect_wifi():
    gc.collect()
    esp.osdebug(None)
    station = network.WLAN(network.STA_IF)  # Create a net status class
    station.active(False)
    time.sleep_ms(20)
    station.active(True)
    station.disconnect()
    time.sleep_ms(20)

    try:
        station.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as error:
        print(error)
    timeout = 20

    while not station.isconnected() and timeout > 0:
        timeout -= 1
        time.sleep_ms(500)

    if station.isconnected():
        print("connected")
    else:
        return


#test_cycle(dial_=dial, button_=button, i2c_=i2c_bus)
#connect_wifi()

