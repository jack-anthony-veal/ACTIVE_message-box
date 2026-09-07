# Wokwi proof

This simulation uses the repository's MicroPython 1.28.0 ESP32/ST7789 firmware,
`Wokwi-GUEST`, RFC2217 port 4000, the production GPIO26/GPIO27 encoder inputs,
and GPIO25 button input.

Wokwi does not document a built-in ST7789 part. `wokwi/main.py` injects a
simulator-only no-op backend through the existing `Display` boundary so serial
markers can test application state deterministically. Production display code
is unchanged, and this setup does not claim LCD visual validation.

Start a simulation and upload the client tree:

```sh
wokwi-cli . --interactive
./tools/upload_wokwi.sh
```

For lint and all automated scenarios:

```sh
curl -L https://wokwi.com/ci/install.sh | sh
export WOKWI_CLI_TOKEN=wok_...
./tools/run_wokwi_tests.sh
```

The upload helper stages a temporary client copy and replaces both ignored
device configuration files with the committed simulator placeholders before
opening the RFC2217 connection, so local credentials are never uploaded.

The two black automation buttons reproduce the documented KY-040 quadrature
pin order because Wokwi automation currently exposes button controls, not a
KY-040 rotation control. The interactive encoder remains wired to the same
production pins.
