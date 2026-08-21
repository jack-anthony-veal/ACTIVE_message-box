# Display Migration Log

## Stage 1 — baseline audit and upstream verification

Files changed:
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Audited the complete repository before display edits.
- Confirmed the active display backend is an SH1106 `FrameBuffer` over I2C and exposes `self.oled`.
- Found direct `.oled` access in the keyboard, Wi-Fi states, menu helpers, settings navigation, and base display helpers.
- Found 128×64 layout assumptions in configuration, menus, keyboard, presets, and Wi-Fi rendering.
- Found character-count wrapping in `libraries/utils/text_tools.py` and `display_device.py`, plus manual Wi-Fi splitting.
- Found bitmap payloads in `libraries/utils/ascii.py`, `config/keymap_layout.py`, and `states/settings/WIFI.py`.
- Inspected upstream `russhughes/st7789_mpy` at commit `0ea2f739319a84225411f69aa85d339c261b8185`.
- Verified the C-module constructor, `init()`, immediate drawing primitives, `text(font, ...)`, `write(...)`, `write_len(...)`, power/sleep methods, 240×320 rotation defaults, and build integration through `st7789/micropython.cmake`.
- Confirmed upstream `WRAP`, `WRAP_H`, and `WRAP_V` are edge-wrapping flags, not paragraph layout.
- Selected the upstream `vga1_8x16.py` bitmap font: fixed 8 px width, 16 px height, the declared 0x20–0x7F glyph range, and approximately 6.7 KB source size.

Validation:
- Baseline test commands were attempted both from the repository root and with `PYTHONPATH=src/client`.
- Existing scripts do not run cleanly from the checked-in layout: several expect the obsolete `src/scripts` tree; further imports fail on working-directory-sensitive `config/network.ini`, missing CPython `ubinascii`, or missing MicroPython modules.
- No display code had been changed when these baseline failures were recorded.

Hardware validation still required:
- All LCD behaviour; no ESP32 or LCD is connected.
- Board firmware version and `import st7789` status; `mpremote` was intentionally not run because the user confirmed no ESP is connected.
- RGB/BGR order, inversion, offsets, orientation, chip-select wiring, and backlight behaviour.

Remaining:
- Implement the abstraction, UI/layout, centralized assets, state migration, host tests, firmware build attempt, and final audit.

## Stage 2 — ST7789 display boundary and shared UI

Files changed:
- `src/client/hardware_devices/display_device.py`
- `src/client/config/display_config.py`
- `src/client/config/ui_config.py`
- `src/client/libraries/sh1106.py` (removed)
- `src/client/libraries/utils/text_layout.py`
- `src/client/fonts/vga1_8x16.py`
- `src/client/fonts/README.md`

Changes:
- Replaced the SH1106/framebuffer implementation with one `Display` abstraction that lazily creates SPI2 and the upstream C `st7789.ST7789` backend.
- Centralized the requested 240×320 portrait geometry, conservative 20 MHz SPI mode-0 configuration, and semantic RGB565 palette.
- Added direct-draw primitive delegation, a compatibility no-op `show()`, power control, fixed-font text measurement, pixel-width paragraph layout, content clipping, menu/navigation/status helpers, Wi-Fi rows, and a run-bitmap renderer with integer scaling.
- Vendored the verified upstream `vga1_8x16` bitmap font with source and licensing attribution. The text path uses upstream `text(font, ...)`; no ST7789 API was invented.
- The driver uses `buffer_size=0`; no full-screen software framebuffer is allocated.

Validation:
- Host fake-backend tests cover primitive delegation, font metrics, clipping, bitmap scaling, and power methods.
- Text tests cover empty, short, exact-fit, multi-line, long-word, multiple-space, punctuation, explicit-newline, and max-line cases.

Hardware validation still required:
- Confirm RGB/BGR order, inversion, offsets, orientation, CS usage, and backlight wiring on the actual module.
- Confirm whether the physical panel needs a different inversion or color-order setting.

Remaining:
- Migrate all state presentation and centralize bitmap payloads.

## Stage 3 — portrait state UI and centralized assets

Files changed:
- `src/client/assets/__init__.py`
- `src/client/assets/bitmaps.py`
- `src/client/libraries/utils/ascii.py` (removed)
- `src/client/config/keymap_layout.py` (removed)
- `src/client/states/` display-facing modules
- `src/client/libraries/utils/menutools.py`
- `src/client/libraries/utils/text_tools.py`
- `src/client/boot.py`
- `src/client/app/app.py`

Changes:
- Moved reusable artwork, navigation, keyboard, and Wi-Fi run masks to one authoritative asset module and removed duplicate payload sources.
- Reworked main menu, preset, notification/error, settings, Wi-Fi, loading, and keyboard rendering for the shared 240×320 layout and semantic colors.
- Preserved rotary selection, button activation, Wi-Fi scan/connect/persistence, state transitions, and keyboard carousel/double-click behaviour.
- Removed all application/state access to `.oled`, SH1106, `FrameBuffer`, display pins, and the ST7789 backend.
- Removed obsolete character-count wrappers; all paragraph layout now goes through the single pixel-measured helper.
- Removed redundant boot-time OLED/input construction. `App` owns the display and input devices.

Validation:
- Client import/state tests use a fake display boundary and require no LCD.
- Five 40 px menu rows plus four 4 px gaps fit inside the 224 px content region.

Hardware validation still required:
- The requested LCD SCK GPIO18 conflicts with the existing rotary encoder clock GPIO18.
- The requested LCD MOSI GPIO23 conflicts with the existing button GPIO23.
- Input pins were not silently reassigned. Wiring and/or pin assignments must be resolved before powering the complete device.

Remaining:
- Build the C module with exact MicroPython 1.28.0 and complete the final audit.

## Stage 4 — host validation

Files changed:
- `src/tests/display_migration_tests.py`
- `src/tests/full_local_tests.py`
- `src/tests/host_tests.py`
- `src/tests/service_edge_tests.py`
- `src/tests/current_regression_tests.py`
- `src/tests/esp32_state_tests.py`
- `src/tests/esp32_tests.py`

Changes:
- Added focused display, geometry, wrapping, RGB565, bitmap, and fake-backend coverage.
- Updated only the test files needed to replace obsolete paths and SH1106 assumptions; host/backend/demo code was left out of scope.

Validation:
- `python3 src/tests/display_migration_tests.py`: 13 passed.
- `python3 src/tests/full_local_tests.py`: 25 passed.
- `python3 src/tests/host_tests.py`: 12 passed.
- `python3 src/tests/service_edge_tests.py`: 8 passed.
- `python3 src/tests/current_regression_tests.py`: 5 passed.
- `git diff --check`: passed after whitespace cleanup.

Hardware validation still required:
- Board-only tests were not run because no ESP is connected.

Remaining:
- Exact-version firmware build and physical bring-up.

## Stage 5 — MicroPython 1.28.0 C-module build

Files changed:
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Built from the exact MicroPython 1.28.0 source release with ESP-IDF v5.5.1 commit `fcae32885b0296b32044cb99ecbdc50d98dddb83`.
- Integrated upstream `st7789_mpy` commit `0ea2f739319a84225411f69aa85d339c261b8185` through `st7789/micropython.cmake`.
- No MicroPython 1.28.0 compatibility patch was required.
- Did not use the upstream MicroPython 1.20.0 prebuilt firmware.
- Did not erase or flash a board.

Validation:
- Build configuration reported `Found User C Module(s): usermod_st7789`.
- Generated module definitions register `MP_QSTR_st7789` and `mp_module_st7789`.
- The complete ESP32_GENERIC image linked successfully; application size was 1,732,288 bytes with 299,328 bytes free in the app partition.
- Merged firmware: `/tmp/message-box-micropython-build/ports/esp32/build-ESP32_GENERIC/firmware.bin`.
- Merged firmware SHA-256: `1b96d660658e9d4736c004a812f0d6113be39c0c3d7969c2eb9984ce9cadd570`.
- Build command (after sourcing ESP-IDF): `make -C /tmp/message-box-micropython-build/ports/esp32 BOARD=ESP32_GENERIC USER_C_MODULES=/tmp/message-box-st7789_mpy/st7789/micropython.cmake -j2`.

Hardware validation still required:
- Boot the custom firmware and confirm `import st7789` on a connected ESP32.
- The artifact is in a temporary build directory and must be copied somewhere persistent before `/tmp` is cleared if it will be used later.

Remaining:
- Physical display and input validation only.

## Stage 6 — final client audit and bring-up checklist

Files changed:
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Repeated the required searches across `src/client`.
- No active client code references `SH1106`, `sh1106`, `.oled`, `OledDisplay`, `draw_wrap_text`, `wrap_text`, or `draw_art`.
- The only `framebuf` search hit is the word “framebuffer” in font documentation explaining that no full-screen framebuffer is allocated.
- The only standalone 128/64 client hits are two source-mask dimensions inside the centralized legacy run artwork; they are asset data, not screen geometry.
- ST7789 and SPI ownership is confined to `hardware_devices/display_device.py` and `config/display_config.py`.
- Reusable bitmap payloads exist only in `assets/bitmaps.py`; the separate font byte payload is the attributed upstream font, not UI artwork.
- No compatibility shim remains between application states and a controller-specific object. `show()` remains intentionally as a direct-draw no-op.
- Repository documentation outside the requested client scope may still describe the former display; it was intentionally not rewritten.

Validation:
- Final host regression set: 63 tests passed across five scripts.
- `mpremote` was not attempted because the user confirmed no ESP is connected.

Hardware validation still required:
- [ ] Resolve the GPIO18/GPIO23 conflicts between LCD SPI and the existing rotary/button wiring.
- [ ] Preserve the built firmware outside `/tmp` if needed.
- [ ] Flash the custom MicroPython 1.28.0 firmware only when explicitly authorized.
- [ ] Verify `import st7789` and the reported MicroPython version.
- [ ] Connect the ST7789V panel and verify 240×320 portrait orientation.
- [ ] Validate RGB/BGR order and inversion.
- [ ] Validate panel offsets and full-edge drawing.
- [ ] Validate CS-connected versus CS-tied wiring.
- [ ] Verify the backlight wiring; no GPIO backlight control is assumed.
- [ ] Exercise status/title/content/navigation regions on the physical panel.
- [ ] Exercise rotary focus, press activation, Wi-Fi lists, presets, errors, notifications, and the keyboard.
- [ ] Check heap and redraw responsiveness during long text, Wi-Fi scans, and bitmap rendering.

Remaining:
- Physical validation cannot be claimed until an ESP32 and LCD are connected and observed.

## Stage 7 — permanent firmware, GPIO resolution, and GMT024-08-SPI8P profile

Files changed:
- `src/client/config/gpio_config.py`
- `src/client/config/gpio.txt`
- `src/client/config/display_config.py`
- `src/client/hardware_devices/input_device.py`
- `src/client/firmware/micropython-1.28.0-esp32-st7789.bin`
- display migration source and test files containing migration-added comments

Changes:
- Copied the merged MicroPython 1.28.0/ST7789 firmware into the repository so it no longer depends on the temporary build directory.
- Centralized the complete GPIO map and recorded the wiring changes in `gpio.txt`.
- Assigned the GMT024-08-SPI8P display to SCL/SCK GPIO18, SDA/MOSI GPIO23, DC GPIO16, RST GPIO4, and CS GPIO5.
- Assigned the rotary encoder to GPIO26/GPIO27, the button to GPIO25, and the wake input to GPIO33.
- Kept the LCD backlight connected to 3.3 V. GPIO32 remains unused and available if controlled backlight support is added later.
- Removed all triple-quoted comment strings from `src/client` and removed comments introduced by the migration.

Validation:
- Exact-module references identify GMT024-08-SPI8P as a 240×320 ST7789V IPS module using 4-wire SPI and 3.3 V logic.
- A published working ESP32 configuration for this module uses SPI mode 0, zero X/Y offsets, inversion enabled, normal RGB order, SCK GPIO18, MOSI GPIO23, DC GPIO16, RST GPIO4, and CS GPIO5. The client now matches these values.
- The published configuration demonstrates 40 MHz; the client remains at the more conservative 20 MHz required for this migration.
- The dedicated configuration test confirms the display and input GPIO sets do not overlap.
- Final host regression set: 64 tests passed across five scripts.
- Permanent firmware SHA-256: `1b96d660658e9d4736c004a812f0d6113be39c0c3d7969c2eb9984ce9cadd570`.
- A CP2102-connected ESP32 was detected at `/dev/ttyUSB0`. One safe version/import probe could not enter Raw REPL and was stopped; it was not retried.

Hardware validation still required:
- No peripherals are attached, so the LCD orientation, colors, inversion, offsets, backlight, and redraw behaviour have not been observed.
- The connected ESP32 has not been erased or flashed.
- The current board firmware version and `import st7789` status remain unknown because Raw REPL did not respond.

Remaining:
- Flash only with explicit authorization, then attach the LCD and perform the Stage 6 physical checklist.

## Stage 8 — external RGB565 UI asset integration

Files changed:
- `src/client/assets/bin/*.bin`
- `src/client/assets/registry.py`
- `src/client/hardware_devices/display_device.py`
- `src/client/states/home/MainMenuState.py`
- `src/client/states/home/LoadingMainMenuState.py`
- `src/client/states/presets/LoadingPresetsState.py`
- `src/client/states/presets/PresetMenu.py`
- `src/client/states/presets/PresetInteract.py`
- `src/client/states/NotifyState.py`
- `src/client/states/settings/WIFI.py`
- `src/client/states/settings/wifi_settings.py`
- `src/client/states/keyboard.py`
- `src/client/states/proc/base_display.py`
- `src/client/libraries/utils/menutools.py`
- `src/tests/display_migration_tests.py`
- `src/tests/full_local_tests.py`
- `src/tests/ui_asset_diagnostics.py`

Changes:
- Added all 82 supplied RGB565 binary assets as external files and one path/width/height metadata registry.
- Added bounded, exact-size file loading and upstream-compatible `blit_buffer` delegation to the Display abstraction.
- Integrated selected menu icons, action icons, loading art, Wi-Fi glyphs, keyboard hints, success art, and five error-family images without direct driver access from states.
- Kept 24x24 Wi-Fi status assets out of the 24 px status region and used 16x16 signal assets at y=4.
- Removed the superseded embedded run-byte artwork module after its active call sites were replaced.
- Corrected error codes 30 through 32 to use the software error family.

Validation:
- All 82 files exist and exactly match width x height x 2 bytes; total asset storage is 180,096 bytes.
- All planned rectangles stay inside the 240x320 status/title/content/navigation regions.
- Planned asset rectangles do not collide; icon/text reservations retain at least 4 px separation.
- The developer diagnostic reports every planned placement as valid.
- Host regression set: 72 tests passed across five scripts.
- No board-side or physical display test was attempted because no peripherals are attached.

Hardware validation still required:
- Confirm the supplied RGB565 byte order, palette backgrounds, colour order, and inversion on the physical GMT024-08-SPI8P panel.
- Observe every integrated screen and confirm optical alignment on the panel.

Remaining:
- 31 supplied alternatives are intentionally unused: decorative alternates, border frames, keyboard selected hints, spinner frames 1 through 7, home/menu/refresh/scan navigation icons, 24x24 status Wi-Fi icons, Wi-Fi cat alternates, and the saved-network icon.

## Stage 9 — remove remaining SH1106 integration and finalize LCD readiness

Files changed:
- `src/client/hardware_devices/display_device.py`
- `src/client/start_up/tests.py`
- `src/client/states/keyboard.py`
- `src/client/states/settings/WIFI.py`
- `src/client/states/settings/wifi_settings.py`
- `src/host/main.py`
- `src/tests/display_migration_tests.py`
- `src/tests/full_local_tests.py`
- `src/tests/host_tests.py`
- `src/tests/esp32_state_tests.py`
- `src/tests/esp32_tests.py`
- `src/tests/resource_audit.py`
- `src/client/fonts/README.md`
- `README.md`

Changes:
- Removed the unused I2C display probe and replaced it with ST7789 C-module and SPI configuration readiness checks.
- Removed the legacy run-bitmap renderer, buffered `show()` compatibility method, and old custom-message compatibility renderer.
- Removed obsolete framebuffer and I2C test shims.
- Updated the host preset geometry limit from the former 16x6 character layout to the current 27x10 ST7789 content layout.
- Updated project documentation to identify the GMTO24-08-SPI8P ST7789V LCD, SPI wiring, and permanent custom firmware.

Validation:
- No active source, test, host, demo, or README references remain for SH1106, OLED, SSD1306, I2C display setup, framebuffer display setup, or 128x64 geometry.
- Application display construction resolves only to `Display`, SPI2, and `st7789.ST7789`.
- Static firmware inspection contains the `st7789` module and ST7789 symbols.
- Permanent firmware SHA-256 remains `1b96d660658e9d4736c004a812f0d6113be39c0c3d7969c2eb9984ce9cadd570`.
- All 82 RGB565 assets and all 56 planned placements remain valid.
- Host preset limits accept 270 characters on one wrapped line and reject 271 with the 240x320 limit message.
- Host regression set: 72 tests passed across five scripts.
- `git diff --check` passed.

Hardware validation still required:
- No LCD or input peripherals are attached, so panel output cannot be observed.
- The connected ESP32 was not flashed or retried after the earlier Raw REPL failure.

Remaining:
- Flash only with explicit authorization, attach the LCD, and validate colour order, inversion, offsets, backlight, and physical rendering.

## Stage 10 — final 45-asset pack integration and connected-board probe

Files changed:
- `message_box_ui_assets_rgb565.zip`
- `src/client/assets/ASSET_LAYOUT.md`
- `src/client/assets/bin/action/*.bin`
- `src/client/assets/bin/menu/*.bin`
- `src/client/assets/bin/navigation/*.bin`
- `src/client/assets/bin/state/*.bin`
- `src/client/assets/bin/status/*.bin`
- `src/client/assets/registry.py`
- `src/client/config/ui_config.py`
- `src/client/hardware_devices/display_device.py`
- display-facing modules under `src/client/states/` and `src/client/libraries/utils/`
- `src/client/diagnostics/lcd_diagnostic.py`
- `src/client/diagnostics/asset_gallery.py`
- `src/client/diagnostics/screen_gallery.py`
- `src/tests/display_migration_tests.py`
- `src/tests/full_local_tests.py`
- `src/tests/ui_asset_diagnostics.py`
- `LCD_HARDWARE_TEST.md`
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Replaced the earlier 82-file candidate pack with the authoritative 45-file RGB565 pack from `message_box_ui_assets_rgb565.zip`.
- Preserved the supplied `ASSET_LAYOUT.md` and exact `action`, `menu`, `navigation`, `state`, and `status` directory hierarchy.
- Reduced the registry to exactly 45 path/width/height records with no embedded pixel data.
- Matched the UI background to the assets' `0x0000` matte and implemented the fixed 24 px status, 32 px title, 224 px content, and 40 px navigation regions.
- Applied exact status, menu, navigation, and state-art coordinates without runtime asset scaling.
- Kept all `blit_buffer` access inside `Display`; application states use high-level display methods and `draw_asset`.
- Added automatic, encoder-independent LCD, 45-asset, and 19-screen diagnostic scripts. These scripts do not run in production and use mock screen data only.
- Preserved production rotary/button support and added host input injection coverage for positive/negative movement, selection wrapping, button selection, and keyboard redraw.
- The superseded 82-file working asset directory was moved to `/tmp/message-box-assets.dRwcUH/legacy-bin-82`; the user's source archives were not modified.

Validation:
- Asset count: 45; total RGB565 bytes: 115840.
- Every file matches `width × height × 2`; 16×16 files are 512 bytes, 24×24 files are 1152 bytes, and 64×64 files are 8192 bytes.
- Registry filenames, metadata, path confinement, matte corners, region containment, non-collision, and fixed padding checks pass.
- Host results: 52 unit tests passed; 5 current-regression checks passed; 12 host-state checks passed; 8 service/input edge checks passed. The screen-gallery layout validator and placement diagnostic also passed.
- Syntax/import checks passed for the registry, UI configuration, Display backend, and all three diagnostics.
- `/dev/ttyUSB0` responded through `mpremote 1.28.0`.
- Detected firmware: MicroPython `v1.28.0 on 2026-04-06`, generic ESP32; free heap after collection: 120400 bytes.
- `import st7789` failed exactly with `ImportError: no module named 'st7789'`.
- The prepared custom firmware remains `src/client/firmware/micropython-1.28.0-esp32-st7789.bin`, SHA-256 `1b96d660658e9d4736c004a812f0d6113be39c0c3d7969c2eb9984ce9cadd570`.
- No firmware was flashed, no filesystem was erased, no credentials were read or overwritten, no network requests were made, and no real messages or data mutations were attempted.

Hardware validation still required:
- Flashing the prepared MicroPython 1.28.0/ST7789 image requires explicit user authorization.
- After flashing, confirm the C-module import and rerun the LCD diagnostic.
- Physically confirm portrait orientation, logical dimensions, all edges/corners, RGB/BGR order, inversion, zero offsets, and text rendering.
- Run and visually confirm all 45 assets and all 19 representative screens.
- Measure heap before and after repeated large-asset draws.
- Physical encoder validation remains deferred because the encoder is not connected.

Remaining:
- Hardware-dependent testing is blocked solely by the connected board firmware lacking the required `st7789` C module.
- The migration is host-complete but must not be described as physically verified until the custom firmware is explicitly flashed and the user confirms the visible output.

## Stage 11 — corrected flash, clean deployment, and device execution

Files changed:
- `src/client/config/ui_config.py`
- `LCD_HARDWARE_TEST.md`
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Read the connected flash header and confirmed the earlier merged firmware had been written 0x1000 bytes too high: its bootloader signature was at `0x2000` instead of `0x1000`.
- With explicit user authorization, wrote the validated merged MicroPython/ST7789 image at address `0x0`; esptool verified the written hash.
- Confirmed MicroPython 1.28.0, the built-in `st7789` module, and 165072 bytes of free heap after boot.
- Removed the only initial filesystem entry, `/boot.py`, leaving the ESP32 filesystem empty before deployment.
- Uploaded 112 deployable files totaling 268741 bytes from `src/client`, excluding the desktop `.venv`, host bytecode caches, and the already-flashed firmware binary.
- Replaced `const(rgb565(...))` declarations with exact RGB565 integer literals after the real MicroPython compiler correctly rejected function calls inside `const`.
- Started the uploaded production application. The encoder remains supported but was not required by any diagnostic.

Validation:
- Client imports, registry imports, and all three developer diagnostics import on the real ESP32.
- Device-side sample reads passed for 16×16 (512 bytes), 24×24 (1152 bytes), and 64×64 (8192 bytes) assets.
- LCD diagnostic completed every stage without an exception; final heap was 113184 bytes.
- Asset gallery completed all 45 assets; final heap was 114976 bytes and minimum heap was 108048 bytes.
- Screen gallery completed all 19 representative screens; final heap was 107712 bytes and minimum heap was 100896 bytes.
- Normal application startup produced one clean ESP32 boot followed by the expected disconnected-network `Message loading error: api error` path. No reboot loop remained.
- Updated host display suite: 23 tests passed after the MicroPython constant correction.

Hardware validation still required:
- User confirmation of the visible orientation, corners, offsets, RGB/BGR order, inversion, asset byte order, matte, and complete-screen layouts.
- Physical encoder timing, direction, debounce, and button behavior remain deferred because the encoder is not connected.

Remaining:
- Keep the application running and collect the user's visual confirmation before marking the physical LCD checklist complete.

## Stage 12 — physical panel confirmation

Files changed:
- `LCD_HARDWARE_TEST.md`
- `DISPLAY_MIGRATION_LOG.md`

Changes:
- Retested the physical LCD after the user checked the production wiring: SCK GPIO18, MOSI GPIO23, DC GPIO16, RESET GPIO4, CS GPIO5, BL/VCC 3.3 V, and common ground.
- Held pure RGB565 red, green, blue, and white screens separately so each channel could be confirmed without timing ambiguity.
- Held a full orientation/offset screen with an outer border, unique corner colors, center lines, and directional labels.
- Began a visible repeat of the asset gallery, stopped it promptly when the user said the output was fine and requested no further repetition, then returned the board to the production application.

Validation:
- User confirmed pure red, green, blue, and white were correct; RGB/BGR configuration remains normal RGB.
- User confirmed black text rendered on the white screen.
- User confirmed portrait orientation, all four edges and corner markers, correct directional placement, and no clipping or mirroring.
- User confirmed the visible assets were fine. The repeat reached 35/45 before interruption; the earlier complete device pass rendered all 45 without exceptions.
- Production application restarted with one clean boot and reached the expected disconnected-network error path without a reset loop.

Hardware validation still required:
- Physical text-wrapping and all 19 complete-screen layouts were not repeated after the wiring correction because the user requested that further galleries stop.
- Assets 36 through 45 were not visually repeated after the wiring correction; their complete device-side pass and file validation succeeded.
- Physical encoder timing, direction, debounce, and button behavior remain deferred because the encoder is not connected.

Remaining:
- No code or display-driver blocker remains. The production application is running.
