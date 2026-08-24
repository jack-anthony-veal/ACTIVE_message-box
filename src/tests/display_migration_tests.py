import os
import re
import subprocess
import sys
import tempfile
import types
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = os.path.join(ROOT, "client")
if CLIENT not in sys.path:
    sys.path.insert(0, CLIENT)

micropython = types.ModuleType("micropython")
micropython.const = lambda value: value
sys.modules.setdefault("micropython", micropython)

from assets.registry import ASSETS, ICONS, PLACEMENTS, REGIONS
from config.config import (
    DISPLAY_COLOR_ORDER,
    DISPLAY_INVERSION,
    DISPLAY_ROTATION,
    DISPLAY_SPI_BAUDRATE,
    DISPLAY_SPI_BUS,
    DISPLAY_SPI_PHASE,
    DISPLAY_SPI_POLARITY,
    BUTTON_PIN,
    DIAL_CLK_PIN,
    DIAL_DT_PIN,
    DISPLAY_CS_PIN,
    DISPLAY_DC_PIN,
    DISPLAY_MOSI_PIN,
    DISPLAY_RESET_PIN,
    DISPLAY_SCK_PIN,
    WAKE_PIN,
    CONTENT_BOTTOM,
    MENU_ROW_HEIGHT,
    MENU_VISIBLE_ROWS,
    NAV_ICON_SLOTS,
    NAV_ICON_Y,
    STATE_ART_Y,
    STATE_TEXT_Y,
    STATUS_ICON_SLOTS,
    STATUS_ICON_Y,
    menu_row_y,
    rgb565,
    visible_window,
)
from hardware_devices.display_device import Display
from libraries.config import Config
from libraries.utils.text_layout import layout_text
from states.proc.base_display import BaseScroll, menu_positions


class FakeBackend:
    def __init__(self):
        self.calls = []

    def _record(self, name, *args):
        self.calls.append((name, args))

    def fill(self, *args): self._record("fill", *args)
    def pixel(self, *args): self._record("pixel", *args)
    def line(self, *args): self._record("line", *args)
    def hline(self, *args): self._record("hline", *args)
    def vline(self, *args): self._record("vline", *args)
    def rect(self, *args): self._record("rect", *args)
    def fill_rect(self, *args): self._record("fill_rect", *args)
    def text(self, *args): self._record("text", *args)
    def blit_buffer(self, *args): self._record("blit_buffer", *args)
    def on(self): self._record("on")
    def off(self): self._record("off")
    def sleep_mode(self, *args): self._record("sleep_mode", *args)


class TestTextLayout(unittest.TestCase):
    @staticmethod
    def measure(value):
        return len(value) * 8

    def test_empty_short_and_exact_fit(self):
        self.assertEqual(layout_text("", 32, self.measure), [""])
        self.assertEqual(layout_text("short", 48, self.measure), ["short"])
        self.assertEqual(layout_text("four", 32, self.measure), ["four"])

    def test_wraps_words_and_long_single_word(self):
        self.assertEqual(
            layout_text("one two three", 56, self.measure),
            ["one two", "three"],
        )
        self.assertEqual(
            layout_text("abcdefghij", 32, self.measure),
            ["abcd", "efgh", "ij"],
        )

    def test_spaces_punctuation_and_newlines(self):
        self.assertEqual(
            layout_text("one   two!", 64, self.measure),
            ["one two!"],
        )
        self.assertEqual(
            layout_text("first\nsecond", 80, self.measure),
            ["first", "second"],
        )

    def test_max_lines_clips(self):
        self.assertEqual(
            layout_text("one two three four", 40, self.measure, max_lines=2),
            ["one", "two"],
        )


class TestGeometry(unittest.TestCase):
    def test_gmt024_08_spi8p_configuration(self):
        self.assertEqual((DISPLAY_SPI_BUS, DISPLAY_SPI_BAUDRATE), (2, 20_000_000))
        self.assertEqual((DISPLAY_SPI_POLARITY, DISPLAY_SPI_PHASE), (0, 0))
        self.assertEqual((DISPLAY_ROTATION, DISPLAY_COLOR_ORDER), (0, 0))
        self.assertTrue(DISPLAY_INVERSION)
        self.assertEqual(
            (
                DISPLAY_SCK_PIN,
                DISPLAY_MOSI_PIN,
                DISPLAY_DC_PIN,
                DISPLAY_RESET_PIN,
                DISPLAY_CS_PIN,
            ),
            (18, 23, 16, 4, 5),
        )
        display_pins = {
            DISPLAY_SCK_PIN,
            DISPLAY_MOSI_PIN,
            DISPLAY_DC_PIN,
            DISPLAY_RESET_PIN,
            DISPLAY_CS_PIN,
        }
        input_pins = {DIAL_CLK_PIN, DIAL_DT_PIN, BUTTON_PIN, WAKE_PIN}
        self.assertEqual(input_pins, {25, 26, 27, 33})
        self.assertFalse(display_pins & input_pins)

    def test_four_menu_rows_match_fixed_layout(self):
        self.assertEqual(MENU_VISIBLE_ROWS, 4)
        self.assertEqual(tuple(menu_row_y(index) for index in range(4)), (68, 116, 164, 212))
        self.assertEqual(MENU_ROW_HEIGHT, 44)
        self.assertEqual(menu_row_y(3) + MENU_ROW_HEIGHT, 256)

    def test_visible_window_and_positions(self):
        self.assertEqual(visible_window(3, 1), (0, 3))
        self.assertEqual(visible_window(8, 4), (2, 6))
        self.assertEqual(menu_positions(8, 4), (
            (2, 0), (3, 1), (4, 2), (5, 3)
        ))

    def test_fixed_status_navigation_and_state_slots(self):
        self.assertEqual(STATUS_ICON_SLOTS, (216, 196, 176))
        self.assertEqual(STATUS_ICON_Y, 4)
        self.assertEqual(NAV_ICON_SLOTS[1], (108,))
        self.assertEqual(NAV_ICON_SLOTS[2], (48, 168))
        self.assertEqual(NAV_ICON_SLOTS[3], (28, 108, 188))
        self.assertEqual(NAV_ICON_SLOTS[4], (18, 78, 138, 198))
        self.assertEqual(NAV_ICON_SLOTS[5], (12, 60, 108, 156, 204))
        self.assertEqual(NAV_ICON_Y, 288)
        self.assertEqual((STATE_ART_Y, STATE_TEXT_Y), (96, 176))

    def test_rgb565_conversion(self):
        self.assertEqual(rgb565(255, 0, 0), 0xF800)
        self.assertEqual(rgb565(0, 255, 0), 0x07E0)
        self.assertEqual(rgb565(0, 0, 255), 0x001F)


class TestDisplayAbstraction(unittest.TestCase):
    def setUp(self):
        self.backend = FakeBackend()
        self.display = Display(backend=self.backend)

    def test_primitives_delegate(self):
        self.display.fill(1)
        self.display.pixel(2, 3, 4)
        self.display.line(1, 2, 3, 4, 5)
        self.assertEqual(self.backend.calls, [
            ("fill", (1,)),
            ("pixel", (2, 3, 4)),
            ("line", (1, 2, 3, 4, 5)),
        ])

    def test_text_uses_verified_bitmap_font_metrics(self):
        self.assertEqual(self.display.measure_text("abcd"), 32)
        self.display.text("ok", 10, 20, 1, 0)
        name, args = self.backend.calls[-1]
        self.assertEqual(name, "text")
        self.assertEqual(args[1:4], ("ok", 10, 20))
        self.assertEqual(args[0].WIDTH, 8)
        self.assertEqual(args[0].HEIGHT, 16)

    def test_text_block_respects_bottom_clipping(self):
        end_y = self.display.draw_text_block(
            "one two three four", 0, 240, 40, line_height=20, bottom=280
        )
        text_calls = [call for call in self.backend.calls if call[0] == "text"]
        self.assertEqual(len(text_calls), 2)
        self.assertEqual(end_y, 280)

    def test_power_methods_use_driver_api(self):
        self.display.power_on()
        self.display.power_off()
        self.assertEqual(self.backend.calls, [
            ("sleep_mode", (False,)),
            ("on", ()),
            ("off", ()),
            ("sleep_mode", (True,)),
        ])

    def test_asset_loader_validates_and_blits_exact_buffer(self):
        display = Display(backend=self.backend, asset_root=CLIENT)
        rect = display.draw_asset("nav_back", 48, 288)
        self.assertEqual(rect, (48, 288, 24, 24))
        name, args = self.backend.calls[-1]
        self.assertEqual(name, "blit_buffer")
        self.assertEqual((len(args[0]),) + args[1:], (1152, 48, 288, 24, 24))

    def test_asset_loader_rejects_wrong_byte_count(self):
        with tempfile.TemporaryDirectory() as directory:
            asset_directory = os.path.join(directory, "assets", "bin")
            os.makedirs(asset_directory)
            path = os.path.join(asset_directory, "bad.bin")
            with open(path, "wb") as output:
                output.write(b"\x00" * 10)
            ASSETS["test_bad"] = ("assets/bin/bad.bin", 16, 16)
            try:
                display = Display(backend=self.backend, asset_root=directory)
                with self.assertRaisesRegex(ValueError, "invalid asset size"):
                    display.draw_asset("test_bad", 0, 0)
            finally:
                del ASSETS["test_bad"]

    def test_asset_loader_rejects_path_escape(self):
        ASSETS["test_escape"] = ("assets/bin/../escape.bin", 16, 16)
        try:
            with self.assertRaisesRegex(ValueError, "outside assets/bin"):
                self.display.draw_asset("test_escape", 0, 0)
        finally:
            del ASSETS["test_escape"]

    def test_navigation_and_status_helpers_use_fixed_slots(self):
        display = Display(backend=self.backend, asset_root=CLIENT)
        display.draw_nav_bar(
            left="Back", right="Send",
            left_icon="nav_back", right_icon="nav_send",
        )
        blits = [call[1] for call in self.backend.calls if call[0] == "blit_buffer"]
        self.assertEqual(tuple(args[1:] for args in blits), (
            (48, 288, 24, 24),
            (168, 288, 24, 24),
        ))
        self.backend.calls.clear()
        display.draw_status_bar(status_asset=("status_wifi_4", "status_sync"))
        blits = [call[1] for call in self.backend.calls if call[0] == "blit_buffer"]
        self.assertEqual(tuple(args[1:] for args in blits), (
            (216, 4, 16, 16),
            (196, 4, 16, 16),
        ))


class TestRawAssets(unittest.TestCase):
    def test_icon_aliases_reference_and_cover_registry(self):
        expected_prefixes = {
            "menu": "menu_",
            "navigation": "nav_",
            "action": "action_",
            "status": "status_",
            "state": "state_",
        }
        referenced_assets = []
        self.assertEqual(set(ICONS), set(expected_prefixes))
        for category_name, category in ICONS.items():
            for asset_name in category.values():
                self.assertIn(asset_name, ASSETS)
                self.assertIsInstance(asset_name, str)
                self.assertTrue(asset_name.startswith(expected_prefixes[category_name]))
                referenced_assets.append(asset_name)
        self.assertEqual(set(referenced_assets), set(ASSETS))
        self.assertEqual(len(referenced_assets), len(set(referenced_assets)))

    def test_registered_files_exist_and_match_rgb565_size(self):
        self.assertEqual(len(ASSETS), 45)
        registered_paths = set()
        for name, metadata in ASSETS.items():
            relative_path, width, height = metadata
            registered_paths.add(relative_path)
            normalised = relative_path.replace("\\", "/")
            self.assertTrue(normalised.startswith("assets/bin/"), name)
            self.assertNotIn("..", normalised.split("/"), name)
            self.assertFalse(os.path.isabs(relative_path), name)
            path = os.path.join(CLIENT, relative_path)
            self.assertTrue(os.path.isfile(path), name)
            self.assertEqual(os.path.getsize(path), width * height * 2, name)
            match = re.search(r"_(\d+)x(\d+)\.bin$", relative_path)
            self.assertIsNotNone(match, name)
            self.assertEqual((width, height), tuple(map(int, match.groups())), name)
        discovered_paths = set()
        asset_root = os.path.join(CLIENT, "assets", "bin")
        for directory, _, filenames in os.walk(asset_root):
            for filename in filenames:
                if filename.endswith(".bin"):
                    full_path = os.path.join(directory, filename)
                    discovered_paths.add(os.path.relpath(full_path, CLIENT))
        self.assertEqual(registered_paths, discovered_paths)

    def test_planned_assets_fit_their_regions(self):
        for screen, name, x, y, region_name in PLACEMENTS:
            _, width, height = ASSETS[name]
            region_x, region_y, region_width, region_height = REGIONS[region_name]
            self.assertGreaterEqual(x, region_x, (screen, name))
            self.assertGreaterEqual(y, region_y, (screen, name))
            self.assertLessEqual(x + width, region_x + region_width, (screen, name))
            self.assertLessEqual(y + height, region_y + region_height, (screen, name))

    def test_planned_assets_do_not_collide(self):
        by_screen = {}
        for screen, name, x, y, region_name in PLACEMENTS:
            _, width, height = ASSETS[name]
            by_screen.setdefault(screen, []).append((name, x, y, width, height))
        for screen, items in by_screen.items():
            for index, first in enumerate(items):
                for second in items[index + 1:]:
                    _, ax, ay, aw, ah = first
                    _, bx, by, bw, bh = second
                    overlap = ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah
                    self.assertFalse(overlap, (screen, first[0], second[0]))

    def test_status_and_nav_assets_have_padding(self):
        for screen, name, x, y, region_name in PLACEMENTS:
            _, width, height = ASSETS[name]
            if region_name == "status":
                self.assertEqual((width, height, y), (16, 16, 4), (screen, name))
            if region_name == "nav":
                self.assertEqual((width, height, y), (24, 24, 288), (screen, name))

    def test_icon_text_spacing_reservations(self):
        self.assertEqual(52 - (20 + 24), 8)
        self.assertEqual(152 - (16 + 128), 8)
        self.assertEqual(176 - (152 + 16), 8)
        self.assertEqual(196 - (176 + 16), 4)
        self.assertEqual(288 - 280, 8)
        self.assertEqual(320 - (288 + 24), 8)
        self.assertEqual(STATE_TEXT_Y - (STATE_ART_Y + 64), 16)

    def test_asset_matte_corners_are_black(self):
        for name, metadata in ASSETS.items():
            relative_path, width, height = metadata
            path = os.path.join(CLIENT, relative_path)
            with open(path, "rb") as source:
                data = source.read()
            corners = (
                data[0:2],
                data[(width - 1) * 2:width * 2],
                data[(height - 1) * width * 2:(height - 1) * width * 2 + 2],
                data[-2:],
            )
            self.assertEqual(corners, (b"\x00\x00",) * 4, name)


class TestMaintainability(unittest.TestCase):
    def test_config_round_trip(self):
        expected = {
            "enabled": True,
            "count": 3,
            "network": {
                "ssid": "Example network",
                "password": "not-a-real-password",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "round-trip.ini")
            Config.write(path, expected)
            self.assertEqual(Config.read(path), expected)

    def test_base_scroll_has_no_settings_content(self):
        path = os.path.join(
            CLIENT, "states", "proc", "base_display.py"
        )
        with open(path, "r") as source:
            implementation = source.read().lower()
        for forbidden in (
            "settings", "account", "device", "wifi", "graphics", "tbd",
            "menu_account", "menu_device", "menu_wifi", "menu_graphics",
        ):
            self.assertNotIn(forbidden, implementation)
        self.assertTrue(callable(BaseScroll(("one", "two"))))

    def test_state_navigator_has_one_canonical_module(self):
        from app.StateNavigator import StateNavigator

        self.assertTrue(callable(StateNavigator))
        self.assertFalse(os.path.exists(os.path.join(
            CLIENT, "states", "proc", "StateNavigator.py"
        )))

    def test_no_tracked_python_cache_files(self):
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=os.path.dirname(ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        tracked = tuple(
            path for path in result.stdout.splitlines()
            if "__pycache__/" in path or path.endswith(".pyc")
        )
        self.assertEqual(tracked, ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
