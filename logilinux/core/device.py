"""
Device abstraction layer - Pythonic wrapper around native devices.
"""

from typing import Callable, Optional, List
from enum import Enum
import _logilinux_native as native
from .events import Event


class DeviceType(Enum):
    """Type of Logitech device."""
    UNKNOWN = native.DeviceType.UNKNOWN
    DIALPAD = native.DeviceType.DIALPAD
    MX_KEYPAD = native.DeviceType.MX_KEYPAD


class DeviceCapability(Enum):
    """Capabilities a device may support."""
    ROTATION = native.DeviceCapability.ROTATION
    BUTTONS = native.DeviceCapability.BUTTONS
    HIGH_RES_SCROLL = native.DeviceCapability.HIGH_RES_SCROLL
    LCD_DISPLAY = native.DeviceCapability.LCD_DISPLAY
    IMAGE_UPLOAD = native.DeviceCapability.IMAGE_UPLOAD


class DeviceInfo:
    """Information about a connected device."""
    
    def __init__(self, native_info: native.DeviceInfo):
        self._native = native_info
    
    @property
    def name(self) -> str:
        """Device name."""
        return self._native.name
    
    @property
    def device_path(self) -> str:
        """System path to device."""
        return self._native.device_path
    
    @property
    def vendor_id(self) -> int:
        """USB vendor ID."""
        return self._native.vendor_id
    
    @property
    def product_id(self) -> int:
        """USB product ID."""
        return self._native.product_id
    
    @property
    def type(self) -> DeviceType:
        """Device type."""
        return DeviceType(self._native.type)
    
    def __repr__(self) -> str:
        return f"DeviceInfo(name='{self.name}', type={self.type.name}, path='{self.device_path}')"


class Device:
    """
    Base device class providing monitoring and event handling.
    
    This wraps the native C++ Device class with a Pythonic interface.
    Supports context manager protocol for automatic cleanup.
    """
    
    def __init__(self, native_device):
        self._native = native_device
        self._python_callback: Optional[Callable[[Event], None]] = None
    
    @property
    def info(self) -> DeviceInfo:
        """Get device information."""
        return DeviceInfo(self._native.get_info())
    
    @property
    def type(self) -> DeviceType:
        """Get device type."""
        return DeviceType(self._native.get_type())
    
    def has_capability(self, capability: DeviceCapability) -> bool:
        """Check if device supports a specific capability."""
        return self._native.has_capability(capability.value)
    
    def set_event_callback(self, callback: Callable[[Event], None]) -> None:
        """
        Set callback for device events.
        
        Args:
            callback: Function that receives Event objects
        """
        self._python_callback = callback
        
        def native_callback(native_event):
            """Bridge native C++ events to Python."""
            if self._python_callback:
                py_event = Event.from_native(native_event)
                self._python_callback(py_event)
        
        self._native.set_event_callback(native_callback)
    
    def start_monitoring(self) -> None:
        """Start monitoring device for events."""
        self._native.start_monitoring()
    
    def stop_monitoring(self) -> None:
        """Stop monitoring device events."""
        self._native.stop_monitoring()
    
    @property
    def is_monitoring(self) -> bool:
        """Check if device is currently being monitored."""
        return self._native.is_monitoring()
    
    def grab_exclusive(self, grab: bool = True) -> bool:
        """
        Grab device exclusively (prevents other applications from receiving events).
        
        Args:
            grab: True to grab exclusively, False to release
            
        Returns:
            True if successful
        """
        return self._native.grab_exclusive(grab)
    
    def __enter__(self):
        """Context manager entry - starts monitoring."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stops monitoring."""
        self.stop_monitoring()
        return False
    
    def __repr__(self) -> str:
        return f"Device({self.info})"


class MXKeypadDevice(Device):
    """
    MX Keypad device with LCD display support.
    
    Extends base Device with LCD key image upload capabilities.
    """
    
    def __init__(self, native_device: native.MXKeypadDevice):
        super().__init__(native_device)
        self._native_keypad = native_device
    
    def initialize(self) -> bool:
        """
        Initialize the MX Keypad LCD interface.
        
        Must be called before using LCD functions.
        
        Returns:
            True if initialization successful
        """
        return self._native_keypad.initialize()
    
    def has_lcd(self) -> bool:
        """Check if this device has LCD capabilities."""
        return self._native_keypad.has_lcd()
    
    def set_key_image(self, key_index: int, jpeg_data: bytes) -> bool:
        """
        Set image for a specific LCD key.
        
        Args:
            key_index: Key index (0-8 for grid buttons)
            jpeg_data: JPEG image data as bytes
            
        Returns:
            True if image was set successfully
        """
        return self._native_keypad.set_key_image(key_index, list(jpeg_data))
    
    def set_key_color(self, key_index: int, r: int, g: int, b: int) -> bool:
        """
        Set solid color for a specific LCD key.
        
        Args:
            key_index: Key index (0-8)
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            True if color was set successfully
        """
        return self._native_keypad.set_key_color(key_index, r, g, b)
    
    def __enter__(self):
        """Context manager - initialize and start monitoring."""
        self.initialize()
        return super().__enter__()
