# logilinux-sdk
Python bindings for LogiLinux - Logitech device library for Linux

Python SDK for interfacing with Logitech Creator devices (MX Dialpad, MX Keypad) on Linux.

## Installation

### Prerequisites

1. Build the C++ driver first:
```bash
cd logilinux-driver
./build.sh
cd ..
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build and install the Python package:
```bash
pip install -e .
```

## Quick Start

```python
import logilinux

# Initialize library and find device
lib = logilinux.Library()
device = lib.find_device(logilinux.DeviceType.DIALPAD)

# Define event callback
def on_event(event):
    if isinstance(event, logilinux.RotationEvent):
        print(f"Rotated: {event.delta} steps, angle: {event.angle}")
    elif isinstance(event, logilinux.ButtonEvent):
        status = "pressed" if event.pressed else "released"
        print(f"Button {event.button_code} {status}")

# Set callback and start monitoring
device.set_event_callback(on_event)
device.start_monitoring()

# Keep running (Ctrl+C to exit)
import time
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    device.stop_monitoring()
```

## API Overview

- `Library()` - Main library interface
- `DeviceType.DIALPAD` / `DeviceType.MX_KEYPAD` - Device type enums
- `Device.find_device(type)` - Find and connect to device
- `Device.set_event_callback(callback)` - Set event handler
- `Device.start_monitoring()` / `Device.stop_monitoring()` - Control monitoring
- `RotationEvent` - Rotation events with `delta` and `angle`
- `ButtonEvent` - Button events with `button_code` and `pressed` state

## Requirements

- Python 3.7+
- pybind11
- Built logilinux C++ library (in logilinux-driver submodule)
