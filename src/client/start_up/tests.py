import gc
import os

import machine
import ujson

from config.config import (
    BUTTON_PIN, DIAL_CLK_PIN, DIAL_DT_PIN, DISPLAY_CS_PIN, DISPLAY_DC_PIN,
    DISPLAY_MOSI_PIN, DISPLAY_RESET_PIN, DISPLAY_SCK_PIN,
    DISPLAY_SPI_BAUDRATE, DISPLAY_SPI_BUS, DISPLAY_SPI_PHASE,
    DISPLAY_SPI_POLARITY, DISPLAY_USE_CS, SCREEN_HEIGHT, SCREEN_WIDTH,
    STARTUP_MIN_FREE_STORAGE_BYTES, WAKE_PIN,
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
            critical=True,
        )
    except Exception as error:
        gc.collect()
        return TestResult(
            "ST7789 driver",
            TestResult.FAIL,
            repr(error),
            critical=True,
        )


def test_display_configuration():
    try:
        display_pins = (
            DISPLAY_SCK_PIN,
            DISPLAY_MOSI_PIN,
            DISPLAY_DC_PIN,
            DISPLAY_RESET_PIN,
        )
        if DISPLAY_USE_CS:
            display_pins += (DISPLAY_CS_PIN,)
        input_pins = (DIAL_CLK_PIN, DIAL_DT_PIN, BUTTON_PIN, WAKE_PIN)

        if DISPLAY_SPI_BUS < 0:
            raise ValueError("display SPI bus must be non-negative")
        if DISPLAY_SPI_BAUDRATE <= 0:
            raise ValueError("display SPI baud rate must be positive")
        if DISPLAY_SPI_POLARITY not in (0, 1) or DISPLAY_SPI_PHASE not in (0, 1):
            raise ValueError("display SPI mode must use binary polarity/phase")
        if SCREEN_WIDTH <= 0 or SCREEN_HEIGHT <= 0:
            raise ValueError("display dimensions must be positive")
        if len(set(display_pins)) != len(display_pins):
            raise ValueError("display pins must be unique")
        if set(display_pins) & set(input_pins):
            raise ValueError("display and input pins must not overlap")

        detail = "SPI{} {}Hz mode {} pins {}".format(
            DISPLAY_SPI_BUS,
            DISPLAY_SPI_BAUDRATE,
            DISPLAY_SPI_POLARITY * 2 + DISPLAY_SPI_PHASE,
            "/".join(str(pin) for pin in display_pins),
        )
        return TestResult(
            "ST7789 configuration",
            TestResult.PASS,
            detail,
            critical=True,
        )
    except Exception as error:
        gc.collect()
        return TestResult(
            "ST7789 configuration",
            TestResult.FAIL,
            repr(error),
            critical=True,
        )


def test_storage():
    original_path = "/.storage_test.tmp"
    renamed_path = "/.storage_test_renamed.tmp"
    expected = {"boot_test": True, "number": 12345, "text": "storage-ok"}

    try:
        with open(original_path, "w") as original:
            original.write(ujson.dumps(expected))
        with open(original_path, "r") as original_read:
            if ujson.loads(original_read.read()) != expected:
                return TestResult(
                    "Storage",
                    TestResult.FAIL,
                    "data corrupted",
                    critical=True,
                )
        os.rename(original_path, renamed_path)
        if ".storage_test_renamed.tmp" not in os.listdir("/"):
            return TestResult(
                "Storage",
                TestResult.FAIL,
                "renamed file was not found",
                critical=True,
            )
        os.remove(renamed_path)
        return TestResult(
            "Storage",
            TestResult.PASS,
            "write/read/rename/delete passed",
            critical=True,
        )
    except Exception as error:
        for path in (original_path, renamed_path):
            try:
                os.remove(path)
            except OSError:
                pass
        return TestResult(
            "Storage",
            TestResult.FAIL,
            repr(error),
            critical=True,
        )


def get_storage_info(path="/"):
    stats = os.statvfs(path)
    block_size = stats[0]
    total_blocks = stats[2]
    free_blocks = stats[3]
    return block_size * total_blocks, block_size * free_blocks


def test_free_storage():
    try:
        total, free = get_storage_info()
        status = (
            TestResult.WARN
            if free < STARTUP_MIN_FREE_STORAGE_BYTES
            else TestResult.PASS
        )
        return TestResult(
            "Free storage",
            status,
            "{} bytes free".format(free),
            data={"total_bytes": total, "free_bytes": free},
        )
    except Exception as error:
        return TestResult("Free storage", TestResult.WARN, repr(error))


def test_button_idle(button):
    try:
        value = button.value()
        if value not in (0, 1):
            return TestResult(
                "Button",
                TestResult.FAIL,
                "GPIO {} not active".format(BUTTON_PIN),
                critical=True,
            )
    except Exception as error:
        return TestResult(
            "Button",
            TestResult.FAIL,
            "GPIO {} read error: {}".format(BUTTON_PIN, error),
            critical=True,
        )
    return TestResult(
        "Button",
        TestResult.PASS,
        "GPIO {} responding".format(BUTTON_PIN),
    )


def test_encoder_idle(encoder):
    try:
        clk = encoder._pin_clk.value()
        dt = encoder._pin_dt.value()
        values = {"clk": clk, "dt": dt}
        if clk not in (0, 1) or dt not in (0, 1):
            return TestResult(
                "Encoder",
                TestResult.FAIL,
                "invalid digital state",
                critical=True,
                data=values,
            )
        if clk == 0 and dt == 0:
            return TestResult(
                "Encoder",
                TestResult.WARN,
                "CLK and DT both low; possible wiring issue",
                data=values,
            )
        return TestResult(
            "Encoder",
            TestResult.PASS,
            "input pins readable",
            data=values,
        )
    except Exception as error:
        return TestResult(
            "Encoder",
            TestResult.FAIL,
            repr(error),
            critical=True,
        )
