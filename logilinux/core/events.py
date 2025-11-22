"""
Event classes - Pythonic wrappers around native event types.

These provide a clean interface matching the C# SDK naming conventions
while adding Python-specific conveniences.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
import _logilinux_native as native


class EventType(Enum):
    """Type of device event."""
    ROTATION = native.EventType.ROTATION
    BUTTON_PRESS = native.EventType.BUTTON_PRESS
    BUTTON_RELEASE = native.EventType.BUTTON_RELEASE
    DEVICE_CONNECTED = native.EventType.DEVICE_CONNECTED
    DEVICE_DISCONNECTED = native.EventType.DEVICE_DISCONNECTED


class RotationType(Enum):
    """Type of rotation input."""
    DIAL = native.RotationType.DIAL
    WHEEL = native.RotationType.WHEEL


class DialpadButton(Enum):
    """Dialpad button identifiers."""
    TOP_LEFT = native.DialpadButton.TOP_LEFT
    TOP_RIGHT = native.DialpadButton.TOP_RIGHT
    BOTTOM_LEFT = native.DialpadButton.BOTTOM_LEFT
    BOTTOM_RIGHT = native.DialpadButton.BOTTOM_RIGHT
    UNKNOWN = native.DialpadButton.UNKNOWN


class MXKeypadButton(Enum):
    """MX Keypad button identifiers (9 LCD grid buttons + navigation)."""
    GRID_0 = native.MXKeypadButton.GRID_0
    GRID_1 = native.MXKeypadButton.GRID_1
    GRID_2 = native.MXKeypadButton.GRID_2
    GRID_3 = native.MXKeypadButton.GRID_3
    GRID_4 = native.MXKeypadButton.GRID_4
    GRID_5 = native.MXKeypadButton.GRID_5
    GRID_6 = native.MXKeypadButton.GRID_6
    GRID_7 = native.MXKeypadButton.GRID_7
    GRID_8 = native.MXKeypadButton.GRID_8
    P1_LEFT = native.MXKeypadButton.P1_LEFT
    P2_RIGHT = native.MXKeypadButton.P2_RIGHT
    UNKNOWN = native.MXKeypadButton.UNKNOWN


@dataclass
class Event:
    """Base event class."""
    type: EventType
    timestamp: int
    
    @classmethod
    def from_native(cls, native_event):
        """Create Python event from native C++ event."""
        if isinstance(native_event, native.RotationEvent):
            return RotationEvent.from_native(native_event)
        elif isinstance(native_event, native.ButtonEvent):
            return ButtonEvent.from_native(native_event)
        elif isinstance(native_event, native.DeviceEvent):
            return DeviceEvent.from_native(native_event)
        else:
            return Event(
                type=EventType(native_event.type),
                timestamp=native_event.timestamp
            )


@dataclass
class RotationEvent(Event):
    """
    Rotation event from dial or wheel.
    
    Attributes:
        rotation_type: Whether this is from DIAL or WHEEL
        delta: Low-resolution rotation delta (steps)
        delta_high_res: High-resolution rotation delta (for smooth scrolling)
        raw_event_code: Raw input event code from device
    """
    rotation_type: RotationType
    delta: int
    delta_high_res: int
    raw_event_code: int
    
    @classmethod
    def from_native(cls, native_event: native.RotationEvent):
        """Create from native RotationEvent."""
        return cls(
            type=EventType.ROTATION,
            timestamp=native_event.timestamp,
            rotation_type=RotationType(native_event.rotation_type),
            delta=native_event.delta,
            delta_high_res=native_event.delta_high_res,
            raw_event_code=native_event.raw_event_code
        )


@dataclass
class ButtonEvent(Event):
    """
    Button press or release event.
    
    Attributes:
        button_code: Raw button code from device
        pressed: True if button was pressed, False if released
    """
    button_code: int
    pressed: bool
    
    @classmethod
    def from_native(cls, native_event: native.ButtonEvent):
        """Create from native ButtonEvent."""
        event_type = EventType.BUTTON_PRESS if native_event.pressed else EventType.BUTTON_RELEASE
        return cls(
            type=event_type,
            timestamp=native_event.timestamp,
            button_code=native_event.button_code,
            pressed=native_event.pressed
        )
    
    def get_dialpad_button(self) -> DialpadButton:
        """Get typed DialpadButton enum if this is from a Dialpad."""
        native_btn = native.get_dialpad_button(self.button_code)
        return DialpadButton(native_btn)
    
    def get_mx_keypad_button(self) -> MXKeypadButton:
        """Get typed MXKeypadButton enum if this is from MX Keypad."""
        native_btn = native.get_mx_keypad_button(self.button_code)
        return MXKeypadButton(native_btn)


@dataclass
class DeviceEvent(Event):
    """
    Device connection/disconnection event.
    
    Attributes:
        device_path: Path to the device that connected/disconnected
    """
    device_path: str
    
    @classmethod
    def from_native(cls, native_event: native.DeviceEvent):
        """Create from native DeviceEvent."""
        return cls(
            type=EventType(native_event.type),
            timestamp=native_event.timestamp,
            device_path=native_event.device_path
        )
