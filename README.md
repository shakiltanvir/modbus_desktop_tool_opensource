# Creative Factory Modbus Workbench

A small, friendly desktop tool for talking to Modbus devices over **RTU (serial)** and **TCP**.
Built with Python, [PySide6](https://doc.qt.io/qtforpython/), and [`pymodbus`](https://github.com/pymodbus-dev/pymodbus).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/shakiltanvir/modbus_desktop_tool_opensource?label=download)](https://github.com/shakiltanvir/modbus_desktop_tool_opensource/releases/latest)
[![CI](https://github.com/shakiltanvir/modbus_desktop_tool_opensource/actions/workflows/ci.yml/badge.svg)](https://github.com/shakiltanvir/modbus_desktop_tool_opensource/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## Features

- Modbus **TCP** and **RTU** connections
- Read coils, discrete inputs, holding registers, and input registers
- Write single or multiple coils
- Write single or multiple registers
- Polling for read functions
- Response summary, value table, and raw response log

## Download

Grab the latest standalone Windows executable — no Python install required — from the
**[Releases page](https://github.com/shakiltanvir/modbus_desktop_tool_opensource/releases/latest)**
(download `ModbusApp.exe`). Or build it yourself / run from source below.

## Requirements

- Python **3.11+**
- Windows (the build script targets Windows; the app itself runs anywhere PySide6 does)

## Run from source

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

On macOS / Linux, activate the venv with `source .venv/bin/activate` instead.

## Build a Windows executable

```powershell
.\build.ps1
```

Output:

- `dist\ModbusApp.exe` — default one-file build
- `dist\ModbusApp\ModbusApp.exe` — if you run `.\build.ps1 -OneDir`

Branding icons (`assets\creative_factory.ico` / `.png`) are generated automatically during the build.

## Usage notes

- For **RTU**, set the correct `COM` port and serial parameters for your device.
- For **TCP**, the default Modbus port is `502`.
- Multiple write values are comma-separated.
- Register values accept decimal or `0x`-prefixed hex.

## Project layout

```
main.py                     # entry point
src/modbus_app/
  app.py                    # application bootstrap
  service.py                # Modbus client / request handling
  worker.py                 # background polling thread
  models.py                 # request/response data models
  branding.py               # theme, colors, generated app icon
  ui/main_window.py         # the Qt UI
tools/generate_brand_assets.py   # writes the .ico/.png used at build time
build.ps1                   # PyInstaller build script (Windows)
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License

Released under the [MIT License](LICENSE).

This project depends on **PySide6 (Qt for Python)**, which is licensed under the
**LGPL-3.0**. PySide6 is installed via `pip` and linked dynamically, so distributing
this app under MIT is fine — but if you redistribute a bundled build, keep PySide6 as
a separately replaceable component and retain its license notice. See the
[Qt licensing FAQ](https://www.qt.io/licensing/) for details.
