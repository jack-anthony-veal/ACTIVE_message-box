# Message Box

Message Box is a two-device ESP32/MicroPython messaging system with a small
FastAPI host. The production device uses a 240×320 ST7789V RGB565 LCD, a rotary
encoder on GPIO26/GPIO27, and a button on GPIO25.

The ESP32 is the application and OTA target. The project does not target or
deploy to a Raspberry Pi, and application OTA never flashes MicroPython or the
ST7789 C-module firmware.

## Device configuration

Credentials and device identity are local files ignored by Git. Copy both
examples before deploying the client:

```sh
cp src/client/config/network.example.ini src/client/config/network.ini
cp src/client/config/device.example.ini src/client/config/device.ini
```

Set `ssid` and `pass` in `network.ini`. Set one shared token plus `owner`,
`peer`, and `base_url` in `device.ini`. The second box swaps owner and peer.
Never commit or print either local file.

For the first application install over USB, first install the repository's
documented MicroPython 1.28.0/ST7789 C-module firmware manually if it is not
already present. With the two local INI files configured, upload the application
tree without flashing firmware:

```sh
./tools/upload_usb.sh
```

The helper removes CPython caches from a temporary staging copy, uploads with
`mpremote`, and resets the board. If an update ever leaves the application
unusable and automatic rollback cannot run, repeat the USB application upload;
do not erase `config/` or `database/`.

## Mailbox behavior

The host stores one JSON slot per sender. Each slot contains an ID, sender,
text, and UTC timestamp. A newer send replaces the sender's previous slot.

- `POST /send/{sender}` replaces that sender's slot.
- `GET /read/{sender}` is non-destructive.
- `POST /ack/{sender}/{id}` clears only a slot with the matching ID.
- `GET/POST /presets/{person}` and `PUT/DELETE /presets/{person}/{index}`
  maintain zero to five presets.

The ESP32 appends a received slot to `database/messages.jsonl`, verifies the
write, deduplicates by ID, and only then acknowledges it. An invalid partial
final JSONL line is ignored and removed before the next append. The Messages
screen opens the newest saved message and formats the server's UTC timestamp as
GMT/BST UK time.

Normal screens start in content mode with their actions hidden. Press opens the
action bar, rotation selects an action, and another press activates it. Keyboard
and loading states are explicit exceptions. Message and preset detail text wrap
by measured pixel width and scroll vertically without truncating stored text.

## Run the host

The host is platform-neutral: any machine or container capable of running
Python and exposing an HTTP(S) endpoint can run it.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r src/host/requirements.txt
export MESSAGE_BOX_TOKEN='the-same-long-random-token-as-device.ini'
uvicorn main:app --app-dir src/host --host 0.0.0.0 --port 8000
```

Use a service manager or container restart policy in production, terminate TLS
at a suitable reverse proxy, and keep `MESSAGE_BOX_TOKEN` in the host's secret
store. The host records no message history or database.

## Startup health

Before Home, the client checks the MicroPython version and ST7789 module,
display construction and 240×320 geometry, GPIO conflicts, heap and free
storage, temporary file operations, device configuration, log access, input
construction, updater recovery, and Wi-Fi/server reachability. Hardware,
storage, configuration, and updater failures block Home. Wi-Fi/server failure
is a warning so cached messages, Settings, and reconnect controls remain usable.

## Application OTA

Package the deployable `src/client` tree on a laptop:

```sh
python tools/package_update.py 0.2.0
```

This publishes `src/host/updates/current/manifest.json` and its verified files.
The host serves the manifest and files through authenticated `/update/*`
routes and retains the newest 100 update results.

The ESP32 checks the manifest during normal startup. Read its bounded result log
at `GET {base_url}/update/results` with the shared token in the `box-token`
header.

At boot, the ESP32 stages every file, checks free space, byte size, and SHA-256,
copies one complete backup, then applies the app update and resets. It preserves
`config/network.ini`, `config/device.ini`, `database/`, and the firmware image.
A successful startup marks the version healthy. If that first health check does
not complete—including when an updated `main.py` cannot import—a stable boot
timer resets the device and the next boot rolls back. `boot.py`,
`app/ota_boot.py`, `app/updater.py`, and the empty `app/__init__.py` are excluded
from remote packages so this recovery path cannot be replaced by an application
update. The previous backup remains until the next update.

## Wokwi

The root `wokwi.toml` uses the checked-in MicroPython 1.28.0/ST7789 firmware and
opens RFC2217 port 4000. The diagram includes an ESP32, Wokwi-GUEST networking,
the encoder GPIOs, and the GPIO25 button. See `wokwi/README.md` for upload and
automation commands.

Wokwi does not document a built-in ST7789 part. The harness injects a
simulator-only display backend and validates serial/state behavior; it does not
replace production display code or claim exact LCD visual validation.

## Verification

```sh
python -m compileall -q src tools
python src/tests/display_migration_tests.py
python src/tests/full_local_tests.py
python src/tests/host_tests.py
python src/tests/host_api_tests.py
python src/tests/service_edge_tests.py
python src/tests/current_regression_tests.py
python src/tests/finish_message_box_tests.py
git diff --check
./tools/run_wokwi_tests.sh
```

The `esp32_*` and resource-audit scripts are board-side checks. Physical LCD,
encoder, and real OTA validation must only be recorded after observation on the
connected hardware.
