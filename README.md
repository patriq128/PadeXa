# PadeXa

Easy to use software and firmware for configuring and customizing your Hackpad.

## Features

- **Easy configuration** — I tried to make the configuration as easy to use as possible, so other people can use PadeXa too.
- **Works without the app** — Every configuration is saved directly to the Hackpad, so you can use it without the app after configuring it.
- **CLI** — For now, the app uses a CLI interface, but it is designed to be simple and easy to use.

## Repository Layout

```text
PadeXa/
├── app/
│   └── main.py       # App runner
└── firmware/
    ├── boot.py       # Storage setup
    └── code.py       # Main firmware
```

## Firmware Usage

> **Note:** For now, the firmware is designed specifically for my Hackpad hardware configuration.

The firmware is based on **CircuitPython**. Your `CIRCUITPY` drive should look something like this:

```text
CIRCUITPY/
├── adafruit_hid/
├── lib/
│   ├── adafruit_bus_device/
│   ├── adafruit_framebuf.mpy
│   └── adafruit_ssd1306.mpy
├── boot.py
├── code.py
└── font5x8.bin
```

> This is not the complete list of files. Some required libraries and modules are already included with CircuitPython.

### Required Libraries

You can get the Adafruit HID library from the [Adafruit CircuitPython HID repository](https://github.com/adafruit/Adafruit_CircuitPython_HID).

The other required libraries can be downloaded from the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20260815/adafruit-circuitpython-bundle-10.x-mpy-20260815.zip).

## Current Hardware Configuration

### 6-Key Matrix

| Matrix | Pin |
| ------ | --- |
| Row 1 | 3 |
| Row 2 | 6 |
| Column A | 0 |
| Column B | 1 |
| Column C | 2 |

### 128×32 OLED Display

| Display | Pin |
| ------- | --- |
| SDA | 4 |
| SCL | 5 |
| VCC | 3V3 |
| GND | GND |

### EC11 Rotary Encoder

| Encoder | Pin |
| ------- | --- |
| A | 10 |
| C | GND |
| B | 9 |
| S1 | GND |
| S2 | 8 |