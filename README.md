# Message-Box

An embedded messaging system built with two ESP32-WROOM devices, GMTO24-08-SPI8P 240×320 ST7789V LCDs, rotary encoders, and a self-hosted FastAPI backend.

## Server Site
projectserver.org

## Repo Tree
```

├── .github
│   └── workflows
│       └── package.yml
├── .idea
│   ├── inspectionProfiles
│   │   └── profiles_settings.xml
│   ├── .gitignore
│   ├── message-box.iml
│   ├── modules.xml
│   └── vcs.xml
├── demo
│   ├── IMG_6451.mov
│   └── IMG_6497.PNG
├── src
│   ├── client
│   │   ├── app
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── app.py
│   │   │   ├── exception_handler.py
│   │   │   └── StateNavigator.py
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── keymap_layout.py
│   │   │   └── network.ini
│   │   ├── database
│   │   │   ├── display.txt
│   │   │   └── preset.txt
│   │   ├── hardware_devices
│   │   │   ├── __init__.py
│   │   │   ├── display_device.py
│   │   │   ├── dummy.py
│   │   │   ├── input_device.py
│   │   │   └── storage.py
│   │   ├── libraries
│   │   │   ├── utils
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ascii.py
│   │   │   │   ├── debug.py
│   │   │   │   ├── menutools.py
│   │   │   │   ├── text_tools.py
│   │   │   │   ├── typing.py
│   │   │   │   └── wifi_status.py
│   │   │   ├── __init__.py
│   │   │   ├── buffer_.py
│   │   │   ├── config.py
│   │   │   ├── rotary_irq_esp.py
│   │   │   ├── rotary.py
│   │   ├── logs
│   │   │   └── errors.txt
│   │   ├── start_up
│   │   │   ├── __init__.py
│   │   │   ├── result.py
│   │   │   └── tests.py
│   │   ├── states
│   │   │   ├── home
│   │   │   │   ├── __init__.py
│   │   │   │   ├── LoadingMainMenuState.py
│   │   │   │   ├── MainMenuState.py
│   │   │   │   ├── MessageState.py
│   │   │   │   └── PresetMenu.py
│   │   │   ├── presets
│   │   │   │   ├── __init__.py
│   │   │   │   ├── LoadingPresetsState.py
│   │   │   │   ├── PresetInteract.py
│   │   │   │   └── PresetMenu.py
│   │   │   ├── proc
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_display.py
│   │   │   │   └── StateNavigator.py
│   │   │   ├── settings
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings_navigate.py
│   │   │   │   ├── wifi_settings.py
│   │   │   │   └── WIFI.py
│   │   │   ├── __init__.py
│   │   │   ├── keyboard.py
│   │   │   └── NotifyState.py
│   │   ├── __init__.py
│   │   ├── boot.py
│   │   └── main.py
│   └── host
│       ├── __pycache__
│       │   └── main.cpython-313.pyc
│       ├── data
│       │   ├── ella.txt
│       │   ├── jack.txt
│       │   └── presets.json
│       ├── static
│       │   └── index.html
│       ├── index.html
│       └── main.py
├── tests
│   ├── __pycache__
│   │   ├── current_regression_tests.cpython-313.pyc
│   │   ├── esp32_regression_tests.cpython-313.pyc
│   │   ├── esp32_state_tests.cpython-313.pyc
│   │   ├── esp32_tests.cpython-313.pyc
│   │   ├── full_local_tests.cpython-313.pyc
│   │   ├── host_tests.cpython-313.pyc
│   │   ├── resource_audit.cpython-313.pyc
│   │   └── service_edge_tests.cpython-313.pyc
│   ├── current_regression_tests.py
│   ├── esp32_regression_tests.py
│   ├── esp32_state_tests.py
│   ├── esp32_tests.py
│   ├── full_local_tests.py
│   ├── host_tests.py
│   ├── resource_audit.py
│   └── service_edge_tests.py
└── README.md
```

## Architecture

`Message-Box A ⇄ FastAPI Server ⇄ Message-Box B`

Each ESP32 runs MicroPython and communicates with the backend over HTTP. The ST7789V LCD provides the interface and the rotary encoder provides navigation and input.

## Hardware

- 2× ESP32-WROOM
- 2× GMTO24-08-SPI8P 240×320 ST7789V LCD
- 2× rotary encoders

## Software

- MicroPython 1.28.0
- Python / FastAPI
- HTTP
- SPI
- Automated tests

## Repository

- `src/` — firmware
- `demo/` — demonstrations
- `tests/` — tests

## Features

- Two-device messaging
- Colour LCD interface
- Rotary encoder navigation
- Menus, presets and settings
- Self-hosted backend

## Setup

1. Flash `src/client/firmware/micropython-1.28.0-esp32-st7789.bin` to both ESP32s.
2. Upload the firmware from `src/`.
3. Configure the API endpoint locally.
4. Start the FastAPI server.
5. Connect both devices to the network.

Keep credentials, Wi-Fi passwords, API keys, tokens and private endpoints out of the repository.

## Status

**Active prototype.**

This project combines embedded firmware, electronics, physical user interfaces, networking, backend development and testing.
