# logilinux-sdk

Pythonic SDK for interfacing with Logitech Creator devices (MX Dialpad, MX Keypad) on Linux. Provides a clean plugin architecture inspired by the official C# SDK but with Python idioms.

## Features

- **Type-safe event system** - Dataclass-based events with full type hints
- **Plugin architecture** - Create reusable plugins with Commands and Adjustments
- **LCD display support** - Upload images to MX Keypad LCD buttons
- **Clean lifecycle management** - Context managers and automatic cleanup
- **Pythonic API** - Follows Python conventions while matching C# SDK naming

## Installation

### Prerequisites

1. Build the C++ driver first:
```bash
cd logilinux-driver
./build.sh
cd ..
```

2. Install Python dependencies and the SDK:
```bash
pip install -r requirements.txt
pip install -e .
```

3. Set library path and permissions (required for runtime):
```bash
# Option 1: Use helper script (handles sudo automatically)
./scripts/run_with_lib.sh examples/simple_monitoring.py

# Option 2: Manual with sudo
export LD_LIBRARY_PATH=$PWD/logilinux-driver/build/lib:$LD_LIBRARY_PATH
sudo -E python examples/simple_monitoring.py

# Option 3: Set up udev rules to avoid needing sudo (recommended)
sudo bash -c 'cat > /etc/udev/rules.d/99-logitech-creative.rules << EOF
# Logitech MX Creative Console - Dialpad
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="bc00", MODE="0666"
# Logitech MX Creative Console - Keypad  
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c354", MODE="0666"
EOF'

sudo udevadm control --reload-rules
sudo udevadm trigger

# After udev rules, no sudo needed:
./scripts/run_with_lib.sh examples/simple_monitoring.py
```

## Quick Start

### Simple Event Monitoring

```python
from logilinux import Library, DeviceType, RotationEvent, ButtonEvent

lib = Library()
device = lib.find_device(DeviceType.DIALPAD)

def on_event(event):
    if isinstance(event, RotationEvent):
        print(f"Dial rotated: {event.delta} steps")
    elif isinstance(event, ButtonEvent):
        print(f"Button {event.button_code} {'pressed' if event.pressed else 'released'}")

device.set_event_callback(on_event)
device.start_monitoring()
```

Run with:
```bash
./scripts/run_with_lib.sh your_script.py
```

### Creating a Plugin

The SDK uses a plugin architecture matching the C# SDK patterns:

```python
from logilinux import Plugin, PluginCommand, PluginAdjustment

class MuteToggle(PluginCommand):
    """Button command that toggles microphone mute."""
    
    def __init__(self):
        super().__init__("Mic Toggle", "Mute/unmute microphone", "Audio")
        self.is_muted = False
    
    def run_command(self, action_parameter=""):
        self.is_muted = not self.is_muted
        # Perform actual mute action here
        self.action_image_changed()  # Update button image
    
    def get_command_image(self, action_parameter="", image_size=PluginImageSize.LARGE):
        # Return PIL Image for LCD button
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (image_size.width, image_size.height))
        draw = ImageDraw.Draw(img)
        
        color = (200, 0, 0) if self.is_muted else (0, 200, 0)
        draw.rectangle([0, 0, image_size.width, image_size.height], fill=color)
        return img


class VolumeControl(PluginAdjustment):
    """Dial adjustment that controls system volume."""
    
    def __init__(self):
        super().__init__("Volume", "System volume", "Audio", has_reset=True)
        self.volume = 50
    
    def apply_adjustment(self, action_parameter="", diff=0):
        self.volume = max(0, min(100, self.volume + diff * 5))
        # Set system volume here
        self.adjustment_value_changed()  # Update display
    
    def run_command(self, action_parameter=""):
        # Reset to 50% when dial is pressed
        self.volume = 50
        self.adjustment_value_changed()
    
    def get_adjustment_value(self, action_parameter=""):
        return f"{self.volume}%"


class MyPlugin(Plugin):
    """Main plugin class."""
    
    def load(self):
        # Initialize resources (API clients, timers, etc.)
        pass
    
    def unload(self):
        # Cleanup resources
        pass
    
    def get_commands(self):
        return [MuteToggle()]
    
    def get_adjustments(self):
        return [VolumeControl()]
```

### Running a Plugin

```python
from logilinux import PluginService, DeviceType

# Create service and register plugin
service = PluginService()
plugin = MyPlugin()
service.register_plugin(plugin)

# Connect to devices
keypad = service.connect_device(DeviceType.MX_KEYPAD)
dialpad = service.connect_device(DeviceType.DIALPAD)

# Assign actions to buttons/dials
mute_cmd = plugin.get_command('MuteToggle')
service.assign_button_action(keypad, 0, mute_cmd)  # Grid button 0

volume_adj = plugin.get_adjustment('VolumeControl')
service.assign_dial_action(dialpad, volume_adj)

# Run
import time
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    service.shutdown()
```

## Architecture

The SDK follows a clean layered architecture:

### C++ Bindings Layer (`_logilinux_native`)
- Thin pybind11 wrapper over logilinux-driver
- Direct 1:1 mapping to C++ API
- No business logic

### Core Layer (`logilinux.core`)
- Pythonic wrappers: `Library`, `Device`, `MXKeypadDevice`
- Type-safe events: `RotationEvent`, `ButtonEvent`, `DeviceEvent`
- Context manager support for automatic cleanup

### Plugin Layer (`logilinux.plugin`)
- `Plugin` base class (matches C# SDK's Plugin)
- `PluginService` for lifecycle management
- Action routing and event handling

### Actions Layer (`logilinux.actions`)
- `PluginCommand` - Button press actions (matches C# SDK's PluginDynamicCommand)
- `PluginAdjustment` - Dial rotation actions (matches C# SDK's PluginDynamicAdjustment)
- Automatic state change notifications

## API Overview

### Core Classes

- `Library()` - Main entry point for device discovery
- `Device` - Base device interface
- `MXKeypadDevice` - MX Keypad with LCD display support

### Device Types

- `DeviceType.DIALPAD` - MX Dialpad (dial + buttons)
- `DeviceType.MX_KEYPAD` - MX Keypad (9 LCD buttons)

### Events

- `RotationEvent` - Dial/wheel rotation with delta and high-res info
- `ButtonEvent` - Button press/release with button codes
- `DeviceEvent` - Device connection/disconnection

### Plugin System

- `Plugin` - Base plugin class with load()/unload() lifecycle
- `PluginCommand` - Button action with run_command() and get_command_image()
- `PluginAdjustment` - Dial action with apply_adjustment() and get_adjustment_value()
- `PluginService` - Service managing plugin lifecycle and device routing

## Examples

See the `examples/` directory:

- `simple_monitoring.py` - Basic event monitoring
- `example_plugin.py` - Full plugin with commands and adjustments

## Requirements

- Python 3.7+
- pybind11
- Pillow (PIL)
- Built logilinux C++ library (in logilinux-driver submodule)

## License

See LICENSE file.
