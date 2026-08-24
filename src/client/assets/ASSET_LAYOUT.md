# Message Box RGB565 Asset Layout

This pack contains **45 raw, headerless RGB565 `.bin` assets** extracted from the three supplied design sheets. Each pixel is stored as two bytes in **big-endian RGB565** order for `russhughes/st7789_mpy` `blit_buffer(buffer, x, y, width, height)`.

The original sheet grid and panel backgrounds were removed to a solid `0x0000` black matte. This matches the dark UI background and avoids visible grid rectangles. Raw RGB565 does not carry transparency.

## Using icons in code

Import the semantic icon-name dictionary from the registry:

```python
from assets.registry import ICONS

ICONS["menu"]["wifi"]
ICONS["navigation"]["back"]
ICONS["status"]["wifi_4"]
```

Pass an icon name to the display helpers; `ASSETS` remains the source of its path and dimensions:

```python
display.draw_asset(ICONS["status"]["wifi_4"], x, y)

display.draw_menu_row(
    row,
    "Wi-Fi",
    icon=ICONS["menu"]["wifi"],
)
```

To discover the available categories and menu icons:

```python
print(ICONS.keys())
print(ICONS["menu"].keys())
```

## Fixed 240×320 layout

| Region | Rectangle `(x, y, w, h)` | Rule |
|---|---:|---|
| Status | `(0, 0, 240, 24)` | Only 16×16 icons; use `y=4` for 4 px top/bottom padding. |
| Title | `(0, 24, 240, 32)` | Text/title only unless a screen specifically needs a 16×16 indicator. |
| Content | `(0, 56, 240, 224)` | Menu rows, screen copy, and 64×64 state art. |
| Navigation | `(0, 280, 240, 40)` | 24×24 icons at `y=288`, giving 8 px top/bottom padding. |

## Scale rules

| Asset role | Stored size | Runtime scale | Placement rule |
|---|---:|---:|---|
| Status | 16×16 | 1× only | `y=4`; right-align in 20 px slots (`x=216, 196, 176…`). |
| Menu/settings | 24×24 | 1× only | In a 44 px row: `x=20`, `y=row_y+10`; text begins at `x=52`. |
| Bottom action | 24×24 | 1× only | `y=288`; use the slot table below. |
| State illustration | 64×64 | 1× only | Default `x=88, y=96`; centred horizontally with room for label/body copy below. |

Do not rescale at runtime. If another size is required, generate a separate `.bin` with nearest-neighbour scaling; runtime scaling costs RAM/CPU and softens pixel art.

### Bottom navigation slot coordinates

| Visible actions | Icon x positions (24 px wide) | y |
|---:|---|---:|
| 1 | `108` | 288 |
| 2 | `48, 168` | 288 |
| 3 | `28, 108, 188` | 288 |
| 4 | `18, 78, 138, 198` | 288 |
| 5 | `12, 60, 108, 156, 204` | 288 |

### Four-row content menu

Rows are `(x=12, width=216, height=44)` at `y=68, 116, 164, 212`, with a 4 px gap. Place each 24×24 icon at `x=20` and `y=row_y+10`; text starts at `x=52`, preserving an 8 px icon/text gap.

## Asset manifest and default coordinates

The default coordinate is a safe reference position, not mandatory business logic. Repeated actions use the applicable slot position from the table above.

| File | Role | Region | Default `(x,y)` | Size | Bytes | Bounds | Notes |
|---|---|---|---:|---:|---:|---|---|
| `bin/menu/home_24x24.bin` | Home/menu icon | content | `(20,78)` | 24×24 | 1152 | PASS | — |
| `bin/menu/messages_24x24.bin` | Messages/menu icon | content | `(20,78)` | 24×24 | 1152 | PASS | — |
| `bin/menu/messages_selected_24x24.bin` | Selected messages icon | content | `(20,78)` | 24×24 | 1152 | PASS | Use only with selected row styling. |
| `bin/menu/presets_24x24.bin` | Presets/menu icon | content | `(20,126)` | 24×24 | 1152 | PASS | — |
| `bin/menu/presets_selected_24x24.bin` | Selected presets icon | content | `(20,126)` | 24×24 | 1152 | PASS | Use only with selected row styling. |
| `bin/menu/settings_24x24.bin` | Settings/menu icon | content | `(20,174)` | 24×24 | 1152 | PASS | — |
| `bin/menu/settings_selected_24x24.bin` | Selected settings icon | content | `(20,174)` | 24×24 | 1152 | PASS | Use only with selected row styling. |
| `bin/menu/wifi_24x24.bin` | Wi-Fi settings icon | content | `(20,78)` | 24×24 | 1152 | PASS | — |
| `bin/menu/device_24x24.bin` | Device settings icon | content | `(20,126)` | 24×24 | 1152 | PASS | — |
| `bin/menu/account_24x24.bin` | Account settings icon | content | `(20,174)` | 24×24 | 1152 | PASS | — |
| `bin/menu/graphics_24x24.bin` | Graphics settings icon | content | `(20,222)` | 24×24 | 1152 | PASS | — |
| `bin/navigation/send_24x24.bin` | Send action | navigation | `(188,288)` | 24×24 | 1152 | PASS | — |
| `bin/navigation/back_24x24.bin` | Back action | navigation | `(28,288)` | 24×24 | 1152 | PASS | — |
| `bin/navigation/change_edit_24x24.bin` | Change/edit action | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/navigation/enter_select_24x24.bin` | Enter/select action | navigation | `(188,288)` | 24×24 | 1152 | PASS | — |
| `bin/status/wifi_0_16x16.bin` | No Wi-Fi signal | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/wifi_1_16x16.bin` | Wi-Fi signal level 1 | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/wifi_2_16x16.bin` | Wi-Fi signal level 2 | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/wifi_3_16x16.bin` | Wi-Fi signal level 3 | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/wifi_4_16x16.bin` | Wi-Fi signal level 4 | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/wifi_error_16x16.bin` | Wi-Fi error | status | `(216,4)` | 16×16 | 512 | PASS | — |
| `bin/status/sync_16x16.bin` | Sync in progress | status | `(196,4)` | 16×16 | 512 | PASS | — |
| `bin/status/alert_16x16.bin` | Warning/alert | status | `(176,4)` | 16×16 | 512 | PASS | — |
| `bin/status/battery_16x16.bin` | Battery state | status | `(196,4)` | 16×16 | 512 | PASS | Only show if real battery telemetry exists. |
| `bin/status/lock_16x16.bin` | Locked state | status | `(176,4)` | 16×16 | 512 | PASS | — |
| `bin/action/refresh_scan_24x24.bin` | Refresh/scan | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/delete_24x24.bin` | Delete | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/plus_add_24x24.bin` | Add item | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/info_24x24.bin` | Information | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/keyboard_24x24.bin` | Open keyboard | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/scroll_24x24.bin` | Scroll hint | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/power_24x24.bin` | Power | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/connected_24x24.bin` | Connected | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/disconnected_24x24.bin` | Disconnected | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/action/question_24x24.bin` | Question/help | navigation | `(108,288)` | 24×24 | 1152 | PASS | — |
| `bin/state/loading_message_64x64.bin` | Loading messages illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/loading_presets_64x64.bin` | Loading presets illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/sending_64x64.bin` | Sending illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/success_64x64.bin` | Success illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/wifi_success_64x64.bin` | Wi-Fi success illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/wifi_error_64x64.bin` | Wi-Fi error illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/http_error_64x64.bin` | HTTP error illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/device_error_64x64.bin` | Device error illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/software_error_64x64.bin` | Software error illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |
| `bin/state/generic_error_64x64.bin` | Generic error illustration | content | `(88,96)` | 64×64 | 8192 | PASS | — |

## Screen-specific mapping

| Screen/state | Asset(s) | Coordinate guidance |
|---|---|---|
| Main/home menu | `messages`, `presets`, `settings` and selected counterparts | 24×24 at `x=20`, `y=row_y+10`; selected art must stay inside the same rectangle. |
| Settings menu | `wifi`, `device`, `account`, `graphics` | 24×24 at `x=20`, `y=row_y+10`. |
| Wi-Fi list/status | `wifi_0`…`wifi_4`, `wifi_error`, `refresh_scan`, `connected`, `disconnected` | Status variant at `(216,4)`; row signal at the existing row trailing slot; actions in bottom nav slots. |
| Keyboard | `keyboard`, `back`, `enter_select`, `change_edit` | 24×24 bottom-action slots only; do not place over the key grid. |
| Presets/messages actions | `send`, `delete`, `plus_add`, `info`, `back` | 24×24 at `y=288`, mapped left-to-right by the number of visible actions. |
| Loading messages | `loading_message` | `(88,96)`; short label below from about `y=176`. |
| Loading presets | `loading_presets` | `(88,96)`; short label below from about `y=176`. |
| Sending | `sending` | `(88,96)`; keep progress copy below the art. |
| Success | `success` | `(88,96)`; keep confirmation copy below the art. |
| Wi-Fi success/error | `wifi_success` or state `wifi_error` | `(88,96)`; use the 64×64 state illustration, not the 16×16 status icon. |
| Error state | `http_error`, `device_error`, `software_error`, `generic_error` | `(88,96)`; title/body copy begins below the art and must wrap inside the content region. |

## Loading with `st7789_mpy`

```python
def draw_bin(tft, path, x, y, width, height):
    expected = width * height * 2
    with open(path, 'rb') as source:
        data = source.read()
    if len(data) != expected:
        raise ValueError('invalid RGB565 bitmap length')
    tft.blit_buffer(data, x, y, width, height)
```

Route this through the project `Display` abstraction rather than calling the ST7789 driver directly from application states.

## Validation summary

- Asset count: **45**
- All output files are validated as exactly `width × height × 2` bytes.
- Every default rectangle is contained within its designated status/content/navigation region.
- 16×16 status icons have 4 px vertical padding inside the 24 px status bar.
- 24×24 navigation icons have 8 px vertical padding inside the 40 px navigation bar.
- 64×64 state art stays fully within the 224 px content region and leaves room for text.
- Battery art is included because it is present in the supplied sheet, but should not be rendered unless the hardware exposes real battery state.
