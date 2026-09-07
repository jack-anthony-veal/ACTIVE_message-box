# AGENTS.md

## Project scope

This repository is the ESP32/MicroPython **Message Box** project.

Current repository structure includes:

- `src/client/` — ESP32/MicroPython client firmware
- `src/client/hardware_devices/display_device.py` — current display abstraction (`OledDisplay`)
- `src/client/states/` — application states and UI rendering
- `src/client/config/` — client configuration
- `src/client/libraries/` — MicroPython support libraries
- `src/tests/` — tests
- `demo/` — demonstrations
- `src/host/` — host/backend-side code

The current display code was written for a **128×64 SH1106 monochrome OLED**. The target display is now a **240×320 ST7789V colour SPI LCD**.

This is a display/UI migration. Do not turn it into an unrelated rewrite.

---

## Authoritative ST7789 driver

Use the upstream project below as the authoritative ST7789 implementation:

`https://github.com/russhughes/st7789_mpy`

Before changing display integration, inspect the upstream README, C-module build instructions, relevant examples, font documentation, and the actual API used by the chosen font type.

Do not invent ST7789 APIs.

Important verified upstream facts:

- `st7789_mpy` is a **C MicroPython user module**, not a normal `st7789.py` file that can simply be copied onto the board.
- The upstream repository currently provides prebuilt generic ESP32 firmware based on **MicroPython 1.20.0**.
- This project targets **MicroPython 1.28.0**.
- Do **not** downgrade the project to the upstream 1.20.0 prebuilt firmware.
- If `import st7789` is unavailable on the current board, determine whether the upstream C module builds against the exact MicroPython 1.28.0 source/tag and document the result.
- If compatibility changes are required for MicroPython 1.28.0, keep them minimal and document them.
- Do not automatically erase or flash the ESP32.
- A custom 1.28.0 firmware build may be required. Build it if the environment permits, but do not flash it without explicit instruction.

The upstream `st7789.WRAP`, `WRAP_H`, and `WRAP_V` options are **edge-wrapping options for graphics/Hershey text**. They are not paragraph/word-wrapping utilities. Do not misuse them as a replacement for line breaking.

The upstream driver provides text/font rendering methods such as `text(...)` and `write(...)`; `write(...)` returns the rendered string width in pixels. Inspect the selected font format and upstream helpers before implementing text measurement or wrapping.

---

## MicroPython target

Production firmware must remain compatible with:

`MicroPython 1.28.0`

Do not introduce CPython-only runtime features into files deployed to the ESP32.

Be conservative with:

- unsupported standard-library modules
- large temporary allocations
- unnecessary object creation
- large framebuffers
- desktop-only typing/runtime dependencies

Do not allocate a full 240×320×16-bit software framebuffer unless a measured requirement justifies it and available heap has been checked.

---

## Display hardware target

Target display:

- Controller: ST7789V
- Resolution: 240×320
- Initial orientation: portrait
- Colour format: RGB565
- Interface: SPI

Use configuration constants for all display pins and SPI settings.

Current intended ESP32 wiring is:

- SPI bus: 2
- SCK: GPIO18
- MOSI: GPIO23
- DC: GPIO2
- RESET: GPIO4
- CS: GPIO5 if the module's CS pin is used
- Backlight: do not assume GPIO control if BL is tied directly to 3.3 V

Start conservatively at **20 MHz SPI** for bring-up. The upstream README warns that ESP32 baud rates above roughly 26.6 MHz require a specific SPI configuration/source modification. Do not default to 40 MHz on an unverified 1.28.0 build.

Module-specific colour order, inversion, and offsets must be treated as hardware-validation items. The upstream driver contains defaults for 240×320, but do not claim a specific physical module is correct until tested.

---

## Display architecture

Application/state code must use the project's display abstraction.

Target dependency direction:

```text
Application / states / menus
            |
            v
     display abstraction
            |
            v
   russhughes st7789_mpy
            |
            v
          SPI
```

Do not merely rename `.oled` to `.lcd`.

Application states must not directly own or manipulate:

- `st7789.ST7789`
- `machine.SPI`
- SH1106
- FrameBuffer
- display GPIO pins

Hardware-specific work belongs behind the display abstraction.

The existing class may be renamed from `OledDisplay` to `Display` if that makes the migration clearer, but preserve imports/callers carefully and update all call sites as one coherent change.

---

## Repository-wide display audit

Before substantial display changes, recursively inspect the complete repository, especially `src/client/`, `src/tests/`, and `demo/`.

Search for all of the following, including indirect aliases:

- `SH1106`
- `sh1106`
- `.oled`
- `framebuf`
- `.text(`
- `.fill(`
- `.fill_rect(`
- `.rect(`
- `.line(`
- `.hline(`
- `.vline(`
- `.pixel(`
- `.show(`
- `.blit(`
- `draw_art`
- `custom_message`
- `draw_wrap_text`
- `wrap_text`
- display-specific `128`
- display-specific `64`

Known legacy hotspots include at least:

- `src/client/hardware_devices/display_device.py`
- `src/client/states/proc/base_display.py`
- `src/client/states/keyboard.py`
- `src/client/states/settings/WIFI.py`
- `src/client/states/settings/wifi_settings.py`
- `src/client/libraries/utils/menutools.py`
- `src/client/states/home/MainMenuState.py`
- `src/client/states/presets/PresetMenu.py`
- `src/client/config/config.py`
- `src/client/libraries/utils/text_tools.py`
- bitmap/run data currently in `src/client/libraries/utils/ascii.py`
- bitmap/run data defined locally in states/config modules

This list is not exhaustive. The recursive audit is authoritative.

After display work, repeat the search and report every intentional remaining legacy reference.

Do not blindly replace the numeric values `128` or `64`; inspect each use and change only values tied to old display geometry.

---

## Display abstraction API

Preserve a small, consistent high-level interface.

The abstraction should expose equivalents for methods actually needed by the app, including where relevant:

- `fill(color)`
- `pixel(x, y, color)`
- `text(...)`
- `line(...)`
- `hline(...)`
- `vline(...)`
- `rect(...)`
- `fill_rect(...)`
- `bitmap(...)` / the central bitmap renderer
- `power_on()`
- `power_off()`
- `show()`

`st7789_mpy` draws directly to the LCD. Therefore `show()` may be a compatibility no-op after direct `.oled.show()` usage has been removed. Keep it only where useful for migration compatibility.

Map old monochrome colours deliberately:

- old `0` must not blindly mean RGB565 `0` in every semantic context
- old `1` must not blindly become an arbitrary nonzero value
- use semantic RGB565 colours through the UI layer

Prefer semantic colour constants over raw RGB565 values in state files.

---

## UI layout

Use a single central UI configuration module, preferably:

`src/client/config/ui_config.py`

Avoid scattering geometry constants through states.

Base portrait layout:

```python
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320

SCREEN_MARGIN = 12

STATUS_HEIGHT = 24
TITLE_HEIGHT = 32
NAV_HEIGHT = 40

CONTENT_TOP = STATUS_HEIGHT + TITLE_HEIGHT      # 56
CONTENT_BOTTOM = SCREEN_HEIGHT - NAV_HEIGHT    # 280
CONTENT_HEIGHT = CONTENT_BOTTOM - CONTENT_TOP  # 224

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24

MENU_X = 12
MENU_WIDTH = 216
MENU_ROW_HEIGHT = 40
MENU_ROW_GAP = 4

ICON_SMALL = 16
ICON_MEDIUM = 24
ICON_LARGE = 32
```

The 40 px row height is intentional: five rows plus four 4 px gaps fit within the 224 px content area.

General screen structure:

```text
┌──────────────────────────────┐
│ status                 24 px │
├──────────────────────────────┤
│ title                  32 px │
├──────────────────────────────┤
│                              │
│ main content          224 px │
│                              │
├──────────────────────────────┤
│ actions/navigation      40 px│
└──────────────────────────────┘
```

Do not blindly scale the old 128×64 coordinates. The aspect ratio and information density are different.

---

## Input/UI principles

The device uses a rotary encoder and button. It is not a touchscreen.

Design around:

- rotate = move focus/selection
- press = activate/select
- clear focus state
- vertical lists where appropriate
- predictable bottom action/navigation area
- colour/background highlighting for the selected item

Do not introduce touch-oriented controls.

Do not change state/input behaviour merely to make the UI prettier unless the change is explicitly required and tested.

For the existing keyboard, preserve the current input semantics by default. Redesign its rendering for 240×320, but do not silently replace the carousel/double-click behaviour with a grid navigation model unless the task explicitly requests that behavioural change.

---

## Colour system

Centralise RGB565 colour constants, preferably in `ui_config.py`.

Use semantic names such as:

```python
COLOR_BACKGROUND
COLOR_SURFACE
COLOR_SURFACE_ALT
COLOR_TEXT
COLOR_TEXT_MUTED
COLOR_PRIMARY
COLOR_SUCCESS
COLOR_WARNING
COLOR_ERROR
COLOR_BORDER
COLOR_SELECTED_BG
COLOR_SELECTED_TEXT
```

Use colour for state, hierarchy, selection, warning, and error. Avoid decorative colour noise.

---

## Text and wrapping

The old project contains character-count-based SH1106 wrapping in `libraries/utils/text_tools.py` and additional hand-written wrapping/layout code in display and Wi-Fi states.

Do not preserve these automatically.

Important: upstream `st7789.WRAP` is **not word wrapping**.

For the new display:

1. inspect the chosen upstream font API;
2. use `st7789_mpy` font rendering directly;
3. use pixel measurements/actual font metrics for line layout;
4. keep exactly one central word/line wrapping helper only if the upstream API does not provide a true paragraph wrapper;
5. remove duplicate SH1106-specific wrappers after all call sites are migrated.

If a helper remains, it must wrap by available pixel width, not by a hard-coded number of characters.

Test at least:

- empty string
- short single line
- exact-fit text
- text that wraps to two or more lines
- long single word
- multiple spaces
- punctuation
- explicit newline
- clipping/max-lines/content-bottom behaviour

Tests must not require a physically connected LCD.

---

## Fonts

Use fonts supported by `russhughes/st7789_mpy`.

Before vendoring or freezing a font module:

- confirm that the font actually exists upstream
- inspect its documented API
- preserve applicable attribution/licensing
- keep the number/size of fonts appropriate for ESP32 flash and heap

Do not invent a font filename.

Use consistent roles such as status/body/title, but functionality is more important than immediately having three separate font families/sizes.

---

## Bitmap/assets policy

All reusable bitmap/icon data must have one authoritative home.

Create:

- `src/client/assets/__init__.py`
- `src/client/assets/bitmaps.py`

Move reusable bitmap/run definitions out of state/config files and out of the current scattered asset locations into `bitmaps.py`.

Known sources include:

- `src/client/libraries/utils/ascii.py`
- local `_WIFI_FACE` and `_WIFI_ICON` data in `src/client/states/settings/WIFI.py`
- keyboard/UI run data in configuration modules
- any other `bytes`/run-length bitmap definitions found by the audit

After migration:

- state files import named assets from `assets.bitmaps`
- no duplicate bitmap payloads remain
- `ascii.py` may be removed if it contains only migrated assets, or retained only as a temporary compatibility re-export with no duplicate bitmap payloads

Preserve the existing run-length format where practical. The current project commonly stores triples:

`(y, x, run_length)`

Centralise the renderer in the display abstraction so old monochrome run assets can be drawn with an RGB565 foreground colour and optional integer scale.

Do not blur pixel art. Use integer nearest-neighbour scaling if scaling is required.

---

## Reusable UI helpers

Prefer a few lightweight helpers over repeated pixel arithmetic:

- `draw_status_bar(...)`
- `draw_title(...)`
- `draw_menu_row(...)`
- `draw_nav_bar(...)`
- `draw_wifi_row(...)`
- `draw_icon(...)`

Do not build a large GUI framework.

States decide:

- what data exists
- what is selected
- what input does
- what state comes next

The display/UI layer decides:

- position
- style
- font
- colour
- rendering details

---

## Wi-Fi UI

Preserve Wi-Fi behaviour unless fixing a demonstrated bug.

Do not unnecessarily rewrite:

- scanning
- sorting
- selection
- credential handling
- connection attempts
- configuration persistence
- state transitions

Move only presentation/display access behind the display abstraction.

Recommended Wi-Fi list geometry:

```python
WIFI_ROW_HEIGHT = 40
WIFI_LIST_X = 8
WIFI_LIST_WIDTH = 224
WIFI_ICON_X = 16
WIFI_NAME_X = 44
WIFI_SIGNAL_X = 198
```

Use a selected-row background/accent rather than SH1106-style inverted 1-bit drawing logic.

---

## Bottom navigation/actions

Reserve the final 40 px for context actions.

Examples:

```text
Back                         Select
Back              Scan       Select
Cancel                        Done
```

Keep the action bar visually consistent across states.

Do not force every screen to show actions that are not available.

---

## `mpremote`

Use `mpremote` for board-side checks when useful.

Prefer:

`python3 -m mpremote`

If that invocation is unavailable but the `mpremote` executable exists, use the executable.

The LCD may be physically disconnected during development. This is expected.

Suitable checks include:

- confirm board/firmware identity
- check MicroPython version
- check whether `import st7789` is available
- copy/import modules that do not require LCD hardware
- run isolated non-display logic where safe

A useful version check is:

```bash
python3 -m mpremote connect auto exec "import sys; print(sys.implementation)"
```

Do not run the full application solely to prove the display works while the LCD is disconnected.

Do not repeatedly retry Raw REPL/connection failures. If `mpremote` cannot establish a stable session, record the failure in the migration log and continue with host-side/static tests.

If `import st7789` fails because the C user module is not present in the installed firmware, treat that as an expected environment result. Do not create a fake production `st7789.py` to hide it.

Do not automatically flash firmware.

---

## Tests

Run existing tests before and after coherent migration stages.

Add host-testable coverage for:

- text wrapping/layout
- menu index calculations
- menu row positions
- content clipping
- bitmap imports and lookup
- bitmap scaling
- RGB565 helper/conversion code if added
- display abstraction behaviour through a fake/mock backend

Mock the hardware boundary rather than the application.

Never claim physical display validation succeeded unless the ST7789V was actually connected and observed.

---

## Migration log

Maintain a root-level file:

`DISPLAY_MIGRATION_LOG.md`

For each meaningful stage, append:

```markdown
## Stage N — title

Files changed:
- ...

Changes:
- ...

Validation:
- ...

Hardware validation still required:
- ...

Remaining:
- ...
```

Keep it concise. Do not paste entire diffs.

Record:

- upstream driver/API findings
- MicroPython 1.28.0 C-module build outcome
- `mpremote` results/failures
- remaining legacy references
- tests executed
- hardware-only uncertainties

---

## Scope protection

Do not unnecessarily rewrite:

- FastAPI/backend communication
- HTTP/API request logic
- message storage
- preset behaviour
- rotary encoder driver
- state-manager architecture
- unrelated network code
- unrelated configuration
- host-side code

Make the smallest coherent changes that complete the display/UI migration.

Do not perform blind repository-wide replacements.

---

## Required verification after display work

Repeat repository-wide searches for:

- `SH1106`
- `sh1106`
- `.oled`
- `framebuf`
- old display-specific `128`
- old display-specific `64`
- duplicate bitmap definitions
- old character-count wrapping helpers

Inspect every remaining occurrence.

Remaining legacy code is acceptable only when intentional and documented.

Report uncertainty instead of guessing about hardware.
