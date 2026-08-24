# Message Box

Message Box is an ESP32/MicroPython messaging device with a 240×320 ST7789V
RGB565 LCD, rotary encoder input, and a FastAPI backend.

## Firmware architecture

The client firmware lives in `src/client/`. Its ownership rules are deliberately
simple:

- `config/config.py` is the one shared source for hardware pins, display
  geometry, colours, timing, limits, storage paths, and state indexes.
- `assets/registry.py::ASSETS` maps asset keys to their path and dimensions.
- `assets/registry.py::ICONS` gives those registered assets readable semantic
  names.
- Each state owns its labels, icons, selection, and transition meanings.
- `Display` owns generic drawing operations; `BaseScroll` owns only scrolling
  and visible-window calculations.
- `libraries/utils/wifi.py` owns shared Wi-Fi interface mechanics. Wi-Fi states
  still own their screens and navigation.

Production firmware targets MicroPython 1.28.0. The ST7789 driver is the
`russhughes/st7789_mpy` C user module frozen into the project firmware; it is
not a deployable `st7789.py` file.

## Adding a menu item

1. Add the label and icon to that screen's state file.
2. Select the icon through `assets.registry.ICONS`.
3. Render the item with the generic `display.draw_menu_row()` helper.

For example:

```python
from assets.registry import ICONS

display.draw_menu_row(
    row_index,
    "Wi-Fi",
    icon=ICONS["menu"]["wifi"],
)
```

## Changing GPIO, layout, or timing

Edit `src/client/config/config.py` only. Startup checks and runtime modules
import the same constants, so hardware values do not need to be repeated in
tests or documentation.

## Local credentials

Copy `src/client/config/network.example.ini` to
`src/client/config/network.ini`, then fill in the local SSID and password.
`network.ini` is ignored by Git and must not be committed or logged.

## Local verification

From the repository root:

```sh
python -m compileall -q src
python src/tests/display_migration_tests.py
python src/tests/full_local_tests.py
python src/tests/host_tests.py
python src/tests/host_api_tests.py
python src/tests/service_edge_tests.py
python src/tests/current_regression_tests.py
```

The `esp32_*` scripts and `resource_audit.py` contain board-only checks and are
not substitutes for observing the physical LCD.

The host API reads its request token from the required `MESSAGE_BOX_TOKEN`
environment variable; it has no source-code default.

## Hardware

- ESP32-WROOM
- GMTO24-08-SPI8P 240×320 ST7789V LCD over SPI
- Rotary encoder and button

The current pin map, SPI settings, and display options are all in
`src/client/config/config.py`.
