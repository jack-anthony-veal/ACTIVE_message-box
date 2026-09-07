import gc
import os
import sys

import machine
import ujson

from config.config import (
    BASE_URL, BUTTON_PIN, DEVICE_OWNER, DEVICE_PEER, DIAL_CLK_PIN, DIAL_DT_PIN,
    DISPLAY_CS_PIN, DISPLAY_DC_PIN, DISPLAY_MOSI_PIN, DISPLAY_RESET_PIN,
    DISPLAY_SCK_PIN, DISPLAY_SPI_BAUDRATE, DISPLAY_SPI_BUS, DISPLAY_SPI_PHASE,
    DISPLAY_SPI_POLARITY, DISPLAY_USE_CS, ERROR_LOG_FILE, SCREEN_HEIGHT,
    SCREEN_WIDTH, STARTUP_MIN_FREE_HEAP_BYTES, STARTUP_MIN_FREE_STORAGE_BYTES,
    TOKEN, WAKE_PIN,
)
from start_up.result import TestResult


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


def _pass(name, message, critical=False, data=None):
    return TestResult(name, TestResult.PASS, message, critical=critical, data=data)


def _fail(name, error, critical=True):
    return TestResult(name, TestResult.FAIL, repr(error), critical=critical)


def _warn(name, error):
    return TestResult(name, TestResult.WARN, str(error), critical=False)


def test_firmware():
    implementation = getattr(sys, "implementation", None)
    name = getattr(implementation, "name", "unknown")
    version = getattr(implementation, "version", ())
    detail = "{} {}".format(name, version)
    if name != "micropython":
        return _warn("Firmware", detail + " (host simulation)")
    if len(version) < 2 or tuple(version[:2]) != (1, 28):
        return _fail("Firmware", "MicroPython 1.28.x required")
    return _pass("Firmware", detail, critical=True)


def test_st7789_driver():
    try:
        import st7789

        getattr(st7789, "ST7789")
        return _pass("ST7789 driver", "C module is available", critical=True)
    except Exception as error:
        return _fail("ST7789 driver", error)
    finally:
        gc.collect()


def _display_pins():
    pins = (DISPLAY_SCK_PIN, DISPLAY_MOSI_PIN, DISPLAY_DC_PIN, DISPLAY_RESET_PIN)
    return pins + (DISPLAY_CS_PIN,) if DISPLAY_USE_CS else pins


def test_display_configuration():
    try:
        if DISPLAY_SPI_BUS < 0 or DISPLAY_SPI_BAUDRATE <= 0:
            raise ValueError("invalid SPI bus or baud rate")
        if DISPLAY_SPI_POLARITY not in (0, 1) or DISPLAY_SPI_PHASE not in (0, 1):
            raise ValueError("invalid SPI mode")
        if (SCREEN_WIDTH, SCREEN_HEIGHT) != (240, 320):
            raise ValueError("display geometry must be 240x320 portrait")
        if len(set(_display_pins())) != len(_display_pins()):
            raise ValueError("display pins must be unique")
        return _pass(
            "ST7789 configuration",
            "SPI{} {}Hz {}x{}".format(
                DISPLAY_SPI_BUS, DISPLAY_SPI_BAUDRATE, SCREEN_WIDTH, SCREEN_HEIGHT
            ),
            critical=True,
        )
    except Exception as error:
        return _fail("ST7789 configuration", error)


def test_pin_conflicts():
    try:
        input_pins = (DIAL_CLK_PIN, DIAL_DT_PIN, BUTTON_PIN, WAKE_PIN)
        if len(set(input_pins)) != len(input_pins):
            raise ValueError("input pins must be unique")
        overlap = set(_display_pins()) & set(input_pins)
        if overlap:
            raise ValueError("display/input pin conflict: " + str(overlap))
        return _pass("Pin conflicts", "none", critical=True)
    except Exception as error:
        return _fail("Pin conflicts", error)


def test_display_construction(display_factory=None):
    try:
        if display_factory is None:
            from hardware_devices.display_device import Display

            display_factory = Display
        display = display_factory()
        if (display.width, display.height) != (SCREEN_WIDTH, SCREEN_HEIGHT):
            raise ValueError("constructed display geometry mismatch")
        del display
        gc.collect()
        return _pass("Display construction", "geometry verified", critical=True)
    except Exception as error:
        return _fail("Display construction", error)


def test_heap():
    try:
        gc.collect()
        free = gc.mem_free()
        if free < STARTUP_MIN_FREE_HEAP_BYTES:
            raise MemoryError("{} bytes free".format(free))
        return _pass("Heap", "{} bytes free".format(free), critical=True)
    except AttributeError as error:
        return _warn("Heap", error)
    except Exception as error:
        return _fail("Heap", error)


def get_storage_info(path="."):
    stats = os.statvfs(path)
    return stats[0] * stats[2], stats[0] * stats[3]


def test_free_storage():
    try:
        total, free = get_storage_info()
        if free < STARTUP_MIN_FREE_STORAGE_BYTES:
            raise OSError("{} bytes free".format(free))
        return _pass(
            "Free storage",
            "{} bytes free".format(free),
            critical=True,
            data={"total_bytes": total, "free_bytes": free},
        )
    except Exception as error:
        return _fail("Free storage", error)


def test_storage():
    original = ".storage-test.tmp"
    renamed = ".storage-test-renamed.tmp"
    expected = {"boot_test": True, "number": 12345}
    try:
        with open(original, "w") as output:
            output.write(ujson.dumps(expected))
        with open(original, "r") as source:
            if ujson.loads(source.read()) != expected:
                raise OSError("temporary data corrupted")
        os.rename(original, renamed)
        with open(renamed, "r") as source:
            if ujson.loads(source.read()) != expected:
                raise OSError("renamed data corrupted")
        os.remove(renamed)
        return _pass("Temporary files", "write/read/rename/delete", critical=True)
    except Exception as error:
        for path in (original, renamed):
            try:
                os.remove(path)
            except OSError:
                pass
        return _fail("Temporary files", error)


def test_configuration():
    try:
        if not TOKEN or not BASE_URL or not DEVICE_OWNER or not DEVICE_PEER:
            raise ValueError("device.ini requires token, owner, peer and base_url")
        if DEVICE_OWNER == DEVICE_PEER:
            raise ValueError("owner and peer must differ")
        if not BASE_URL.startswith(("http://", "https://")):
            raise ValueError("base_url must use HTTP or HTTPS")
        return _pass(
            "Configuration",
            "{} -> {} via {}".format(DEVICE_OWNER, DEVICE_PEER, BASE_URL),
            critical=True,
        )
    except Exception as error:
        return _fail("Configuration", error)


def test_log_access():
    try:
        parent = ERROR_LOG_FILE.replace("\\", "/").rsplit("/", 1)[0]
        current = ""
        for part in parent.split("/"):
            if not part or part == ".":
                continue
            current = current + "/" + part if current else part
            try:
                os.mkdir(current)
            except OSError:
                pass
        with open(ERROR_LOG_FILE, "a") as output:
            output.write("STARTUP|log-access\n")
        with open(ERROR_LOG_FILE, "r") as source:
            source.read()
        return _pass("Log access", "append/read", critical=True)
    except Exception as error:
        return _fail("Log access", error)


def test_input_construction(input_factory=None):
    try:
        if input_factory is None:
            from hardware_devices.input_device import Button, Dial

            button, dial = Button(), Dial()
        else:
            button, dial = input_factory()
        if button is None or dial is None:
            raise ValueError("input factory returned no device")
        return _pass("Input construction", "button and encoder", critical=True)
    except Exception as error:
        return _fail("Input construction", error)


def test_updater_recovery(updater, recovery_status):
    try:
        if recovery_status not in ("normal", "first_boot", "rolled_back"):
            raise ValueError("invalid updater recovery state")
        state = updater.state()
        if type(state) is not dict:
            raise ValueError("invalid updater state file")
        return _pass("Updater recovery", recovery_status, critical=True)
    except Exception as error:
        return _fail("Updater recovery", error)


def test_wifi_server(api):
    try:
        import network

        if not network.WLAN(network.STA_IF).isconnected():
            return _warn("Wi-Fi/server", "Wi-Fi offline")
        api.read_new_message()
        return _pass("Wi-Fi/server", "reachable")
    except Exception as error:
        return _warn("Wi-Fi/server", error)


def run_startup_tests(
    updater,
    recovery_status,
    display_factory=None,
    input_factory=None,
    api=None,
):
    results = [
        test_firmware(),
        test_st7789_driver(),
        test_display_configuration(),
        test_pin_conflicts(),
        test_display_construction(display_factory),
        test_heap(),
        test_free_storage(),
        test_storage(),
        test_configuration(),
        test_log_access(),
        test_input_construction(input_factory),
        test_updater_recovery(updater, recovery_status),
    ]
    if api is not None:
        results.append(test_wifi_server(api))
    return results


def emit_results(results):
    for result in results:
        print("STARTUP|{}|{}|{}".format(result.status, result.name, result.message))
    return not any(result.critical and result.status == TestResult.FAIL for result in results)


def test_button_idle(button):
    try:
        value = button.value()
        if value not in (0, 1):
            raise ValueError("invalid button value")
        return _pass("Button", "GPIO {} responding".format(BUTTON_PIN))
    except Exception as error:
        return _fail("Button", error)


def test_encoder_idle(encoder):
    try:
        values = {"clk": encoder._pin_clk.value(), "dt": encoder._pin_dt.value()}
        if values["clk"] not in (0, 1) or values["dt"] not in (0, 1):
            raise ValueError("invalid encoder value")
        return _pass("Encoder", "input pins readable", data=values)
    except Exception as error:
        return _fail("Encoder", error)
