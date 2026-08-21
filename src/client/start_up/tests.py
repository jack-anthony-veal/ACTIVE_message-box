import gc
from start_up.result import TestResult
import os
import ujson
import urequests as requests
import machine
import config.config as config
from libraries.buffer_ import StaticBuffer
from micropython import const

RESET_NAMES = {
    getattr(machine, "PWRON_RESET", -1): "power_on",
    getattr(machine, "HARD_RESET", -2): "hard_reset",
    getattr(machine, "WDT_RESET", -3): "watchdog",
    getattr(machine, "DEEPSLEEP_RESET", -4): "deep_sleep",
    getattr(machine, "SOFT_RESET", -5): "soft_reset",
}


def get_reset_reason():
    cause = machine.reset_cause()
    return RESET_NAMES.get(cause, "unknown_{}".format(cause))

def fetch_api_token():
    buf = b'\xdd\x1f0\xe3\x07\xe9;Kx9\x1e\x07U\x8a\xbdG\xb3\xa4\xd4p'
    buf2=b'\x1d\x86\x94\xe1\xc8<\xfd\x07(\xdf\xb7\x86;(d\xe6 \xbe\x1f\xb7\xd3\xe0%3'
    def get_token(token, buf):

        return str("".join(chr(t ^ k) for t, k in zip(token, buf)))

    TOKEN_HASH = const(b'\xbehF\x870\xaaH\x1d\x1f@g1-\xf2\xdf?\xc6\xd4\xb3\x07')
    TOKEN_: str = get_token(TOKEN_HASH, buf)
    URL_HASH = const(b'u\xf2\xe0\x91\xf2\x13\xd2wZ\xb0\xdd\xe3X\\\x17\x83R\xc8z\xc5\xfd\x8fWT')
    SERVER_: str = get_token(URL_HASH, buf2)
    config.TOKEN = const(TOKEN_)
    config.SERVER_URL = const(SERVER_)
    del TOKEN_
    del SERVER_
    gc.collect()

def test_api_endpoint(api_endpoint):
    try:
        success = os.system("ping -c {} 1".format(api_endpoint))
        if not success:
            del success
            gc.collect()
            return TestResult("Server", TestResult.WARN, message="PING -C Failed")
    except Exception:
        gc.collect()
        return TestResult("Server", TestResult.WARN, message="PING -C Failed")

    try:
        response = requests.get(api_endpoint, timeout=5)
        if int(response.status_code) > 299 or int(response.status_code) < 199:
            try:
                response.close()
            except Exception:
                pass
            del response
            gc.collect()
            return TestResult("HTTP Server", TestResult.WARN, message="HTTP1/1 GET Failed")
    except Exception:
        gc.collect()
        return TestResult("HTTP Server", TestResult.WARN, message="HTTP1/1 GET Failed")
    finally:
        try:
            response.close()
        except Exception:
            pass

    return TestResult("HTTP Server", TestResult.PASS, "HTTP1/1 GET & ICMP probe Success!")

def test_st7789_driver():
    try:
        import st7789
        driver = getattr(st7789, "ST7789")
        del driver, st7789
        gc.collect()
        return TestResult(
            "ST7789 driver",
            TestResult.PASS,
            "C module is available",
            critical=True
        )
    except Exception as error:
        gc.collect()
        return TestResult(
            "ST7789 driver",
            TestResult.FAIL,
            repr(error),
            critical=True
        )


def test_display_configuration():
    try:
        from config.display_config import (
            DISPLAY_SPI_BAUDRATE, DISPLAY_SPI_BUS, DISPLAY_SPI_PHASE,
            DISPLAY_SPI_POLARITY,
        )
        from config.gpio_config import (
            DISPLAY_CS_PIN, DISPLAY_DC_PIN, DISPLAY_MOSI_PIN,
            DISPLAY_RESET_PIN, DISPLAY_SCK_PIN,
        )
        pins = (
            DISPLAY_SCK_PIN, DISPLAY_MOSI_PIN, DISPLAY_DC_PIN,
            DISPLAY_RESET_PIN, DISPLAY_CS_PIN,
        )
        valid = (
            DISPLAY_SPI_BUS == 2
            and DISPLAY_SPI_BAUDRATE == 20_000_000
            and DISPLAY_SPI_POLARITY == 0
            and DISPLAY_SPI_PHASE == 0
            and pins == (18, 23, 16, 4, 5)
            and len(set(pins)) == len(pins)
        )
        if not valid:
            raise ValueError("unexpected ST7789 SPI configuration")
        return TestResult(
            "ST7789 configuration",
            TestResult.PASS,
            "SPI2 20MHz mode 0 pins 18/23/16/4/5",
            critical=True
        )
    except Exception as error:
        gc.collect()
        return TestResult(
            "ST7789 configuration",
            TestResult.FAIL,
            repr(error),
            critical=True
        )

def test_storage():
    original_path = "/.storage_test.tmp"
    renamed_path = "/.storage_test_renamed.tmp"

    expected = {
        "boot_test": True,
        "number": 12345,
        "text": "storage-ok"
    }

    try:
        with open(original_path, "w") as original:
            data = ujson.dumps(expected)
            original.write(data)
            del data, original



        with open(original_path, "r") as original_read:
            data = original_read.read()
            decoded = ujson.loads(data)
            if decoded != expected:
                del data
                original_read.close()
                del original_read
                return TestResult(name='storage',
                                  status=TestResult.FAIL, message="data corrupted",
                                  critical=True
                                  )


        os.rename(original_path, renamed_path)
        files = os.listdir("/")
        if ".storage_test_renamed.tmp" not in files:
            del files
            return TestResult(
                "Storage",
                TestResult.FAIL,
                "Renamed file was not found",
                critical=True
            )

        os.remove(renamed_path)
        del files
        return TestResult(
            "Storage",
            TestResult.PASS,
            "Write/read/rename/delete passed",
            critical=True
        )

    except Exception as error:
        for path in (original_path, renamed_path):
            try:
                os.remove(path)
            except OSError:
                pass

        del path
        return TestResult(
            "Storage",
            TestResult.FAIL,
            repr(error),
            critical=True
        )

def get_storage_info(path="/"):
    stats = os.statvfs(path)
    block_size = stats[0]
    total_blocks = stats[2]
    free_blocks = stats[3]
    total_bytes = block_size * total_blocks
    free_bytes = block_size * free_blocks
    return total_bytes, free_bytes

def test_free_storage():
    try:
        total, free = get_storage_info()

        if free < 16_384:
            return TestResult(
                "Free storage",
                TestResult.WARN,
                "Only {} bytes free".format(free),
                data={
                    "total_bytes": total,
                    "free_bytes": free
                }
            )

        return TestResult(
            "Free storage",
            TestResult.PASS,
            "{} bytes free".format(free),
            data={
                "total_bytes": total,
                "free_bytes": free
            }
        )

    except Exception as error:
        return TestResult(
            "Free storage",
            TestResult.WARN,
            repr(error)
        )
def test_button_idle(button):
    try:
        value = button.value()
        if value not in (1,0):
            del value
            return TestResult("Button",
                              TestResult.FAIL,
                              message="PIN 23 not active", critical=True
                              )

    except Exception as error:
        return TestResult(
            "Button", TestResult.FAIL, message="PIN 23 error reading", critical=True
        )

    del value
    return TestResult("Button",TestResult.PASS, message="PIN 23 Responding")


def test_encoder_idle(encoder):
    try:
        clk = encoder._pin_clk.value()
        dt = encoder._pin_dt.value()


        values = {
            "clk": clk,
            "dt": dt,
        }

        if clk not in (0, 1) or dt not in (0, 1):
            value_ = values
            del clk, dt, encoder, values
            return TestResult(
                "Encoder",
                TestResult.FAIL,
                "Invalid digital state",
                critical=True,
                data=value_
            )

        if clk == 0 and dt == 0:
            value_ = values
            del clk, dt, encoder, values
            return TestResult(
                "Encoder",
                TestResult.WARN,
                "CLK and DT both low; possible wiring issue",
                data=value_
            )
        value_ = values
        del clk, dt, encoder, values
        return TestResult(
            "Encoder",
            TestResult.PASS,
            "Input pins readable",
            data=value_
        )

    except Exception as error:
        return TestResult(
            "Encoder",
            TestResult.FAIL,
            repr(error),
            critical=True
        )
