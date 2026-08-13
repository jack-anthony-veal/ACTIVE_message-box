# Message-Box

An embedded messaging system built with two ESP32-WROOM devices, SH1106 128×64 OLED displays, rotary encoders, and a self-hosted FastAPI backend.

## Architecture

`Message-Box A ⇄ FastAPI Server ⇄ Message-Box B`

Each ESP32 runs MicroPython and communicates with the backend over HTTP. The OLED provides the interface and the rotary encoder provides navigation and input.

## Hardware

- 2× ESP32-WROOM
- 2× SH1106 128×64 OLED
- 2× rotary encoders

## Software

- MicroPython 1.28.0
- Python / FastAPI
- HTTP
- I²C
- Automated tests

## Repository

- `src/` — firmware
- `demo/` — demonstrations
- `tests/` — tests

## Features

- Two-device messaging
- OLED interface
- Rotary encoder navigation
- Menus, presets and settings
- Self-hosted backend

## Setup

1. Flash MicroPython 1.28.0 to both ESP32s.
2. Upload the firmware from `src/`.
3. Configure the API endpoint locally.
4. Start the FastAPI server.
5. Connect both devices to the network.

Keep credentials, Wi-Fi passwords, API keys, tokens and private endpoints out of the repository.

## Status

**Active prototype.**

This project combines embedded firmware, electronics, physical user interfaces, networking, backend development and testing.
