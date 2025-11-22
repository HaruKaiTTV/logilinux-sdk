"""
LogiLinux Python SDK

Python SDK for interfacing with Logitech Creator devices on Linux.

This SDK provides a clean, Pythonic API for creating plugins that control
the MX Creative Console (Dialpad + Keypad) and other Logitech devices.

Architecture follows the C# SDK naming conventions while using Python idioms.

Quick Start:
    >>> from logilinux import Library, DeviceType
    >>> 
    >>> lib = Library()
    >>> device = lib.find_device(DeviceType.DIALPAD)
    >>> 
    >>> def on_event(event):
    ...     print(f"Event: {event}")
    >>> 
    >>> device.set_event_callback(on_event)
    >>> device.start_monitoring()

For plugin development:
    >>> from logilinux import Plugin, PluginCommand, PluginAdjustment
    >>> 
    >>> class MyCommand(PluginCommand):
    ...     def run_command(self, action_parameter=""):
    ...         print("Button pressed!")
    >>> 
    >>> class MyPlugin(Plugin):
    ...     def get_commands(self):
    ...         return [MyCommand()]
"""

__version__ = '0.1.0'

# Core components
from .core import (
    Library,
    Device,
    Event,
    RotationEvent,
    ButtonEvent,
    DeviceEvent,
)

from .core.device import (
    DeviceType,
    DeviceCapability,
    DeviceInfo,
    MXKeypadDevice,
)

from .core.events import (
    EventType,
    RotationType,
    DialpadButton,
    MXKeypadButton,
)

# Plugin system
from .plugin import (
    Plugin,
    PluginService,
)

# Actions
from .actions import (
    PluginAction,
    PluginCommand,
    PluginAdjustment,
    PluginImageSize,
)

__all__ = [
    # Core
    'Library',
    'Device',
    'MXKeypadDevice',
    'DeviceType',
    'DeviceCapability',
    'DeviceInfo',
    
    # Events
    'Event',
    'RotationEvent',
    'ButtonEvent',
    'DeviceEvent',
    'EventType',
    'RotationType',
    'DialpadButton',
    'MXKeypadButton',
    
    # Plugin system
    'Plugin',
    'PluginService',
    
    # Actions
    'PluginAction',
    'PluginCommand',
    'PluginAdjustment',
    'PluginImageSize',
]
