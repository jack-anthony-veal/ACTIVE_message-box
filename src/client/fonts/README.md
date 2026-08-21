# Display font

`vga1_8x16.py` is copied from
[`russhughes/st7789_mpy`](https://github.com/russhughes/st7789_mpy) at commit
`0ea2f739319a84225411f69aa85d339c261b8185`. It is one of the bitmap fonts
documented for the driver's `text(font, ...)` API and is covered by the
upstream repository's MIT licence.

The fixed 8×16 metrics keep layout measurement deterministic and use a small
amount of ESP32 flash. The driver renders one character with a temporary
8×16×2-byte RGB565 buffer; no screen-sized RGB565 buffer is allocated.
