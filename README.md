# Requirements
2x ESP-32
2x SH1106 Oled 128x64
2x Digital Rotary Encoder
1x Self-Hosted API endpoint for routing communications

# Setup
Flash each ESP with Micropython 1.28.0 using esptool
Upload the files from the repo to the device
In config.py and api.py configure the HTTP routes to be suitable for your own endpoints
Now enjoy your messaging device!!

# Program Details / Functions
Main Menu state to cycle through Messages, Presets and Settings
... TBC