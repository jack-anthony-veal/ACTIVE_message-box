# LCD Hardware Test

Device detected: `/dev/ttyUSB0`

Board probe:

- MicroPython: `v1.28.0 on 2026-04-06`
- Machine: `Generic ESP32 module with ESP32`
- Free heap after corrected firmware boot: `165072` bytes
- ST7789 import: passed, built-in module present
- Prepared custom firmware: `src/client/firmware/micropython-1.28.0-esp32-st7789.bin`
- Prepared firmware SHA-256: `1b96d660658e9d4736c004a812f0d6113be39c0c3d7969c2eb9984ce9cadd570`

The first user flash placed the merged image at `0x1000`, shifting its bootloader to `0x2000` and causing an `invalid header: 0xffffffff` boot loop. With explicit authorization, the validated merged image was written at its required `0x0` address and its hash was verified. The ESP32 filesystem was then emptied, 112 deployable client files were uploaded, and the normal application was started.

- [x] ST7789 C module present
- [x] MicroPython 1.28.0 confirmed
- [x] LCD initialises
- [x] portrait orientation correct
- [x] 240×320 logical dimensions correct
- [x] RGB/BGR order correct
- [x] inversion correct
- [x] offsets correct
- [x] full-screen border visible
- [x] all four corners visible
- [x] text renders
- [ ] text wrapping correct — HOST PASS; DEVICE RAN; VISUAL CONFIRMATION PENDING
- [ ] all 45 assets render — DEVICE PASS ALL 45; USER CONFIRMED REPEAT THROUGH 35/45 AND REQUESTED STOP
- [x] asset colours correct — USER CONFIRMED VISIBLE REPEAT
- [x] asset matte matches background — USER CONFIRMED VISIBLE REPEAT
- [ ] menu layouts correct — DEVICE RAN; VISUAL CONFIRMATION PENDING
- [ ] Wi-Fi layouts correct — DEVICE RAN; VISUAL CONFIRMATION PENDING
- [ ] keyboard layout correct — DEVICE RAN; VISUAL CONFIRMATION PENDING
- [ ] loading screens correct — DEVICE RAN; VISUAL CONFIRMATION PENDING
- [ ] error screens correct — DEVICE RAN; VISUAL CONFIRMATION PENDING
- [x] memory remains stable — asset minimum `108048`; screen minimum `100896` bytes
- [ ] physical encoder tested — DEFERRED — encoder not connected

Completed device-side sequence:

1. Confirmed MicroPython 1.28.0 and `import st7789`.
2. Ran `src/client/diagnostics/lcd_diagnostic.py` without exceptions; final heap `113184` bytes.
3. Ran all 45 entries in `src/client/diagnostics/asset_gallery.py`; final/minimum heap `114976/108048` bytes.
4. Ran all 19 entries in `src/client/diagnostics/screen_gallery.py`; final/minimum heap `107712/100896` bytes.
5. Started the production `main.py`; one clean boot was observed and the disconnected network produced the expected API error path.

The user physically confirmed pure red, green, blue, and white; black text on white; portrait orientation; full border; all four corner markers; correct top/bottom/left/right placement; and no clipping or mirroring. During the repeat asset gallery the user reported that everything was fine and asked to stop; the process was interrupted after asset 35/45. All 45 assets had already completed device-side rendering without exceptions in the earlier automated pass.
