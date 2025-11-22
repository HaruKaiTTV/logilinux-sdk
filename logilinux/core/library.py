"""
Library class - Main entry point for device discovery.
"""

from typing import List, Optional
import _logilinux_native as native
from .device import Device, DeviceType, MXKeypadDevice


class Library:
    """
    Main library interface for device discovery and management.
    
    This is the primary entry point for the LogiLinux SDK.
    Create an instance to discover and connect to Logitech devices.
    
    Example:
        >>> lib = Library()
        >>> device = lib.find_device(DeviceType.DIALPAD)
        >>> if device:
        ...     device.set_event_callback(my_callback)
        ...     device.start_monitoring()
    """
    
    def __init__(self):
        """Initialize the LogiLinux library."""
        self._native = native.Library()
    
    def discover_devices(self) -> List[Device]:
        """
        Discover all connected Logitech devices.
        
        Returns:
            List of Device objects for all found devices
        """
        native_devices = self._native.discover_devices()
        return [self._wrap_device(d) for d in native_devices]
    
    def find_device(self, device_type: DeviceType) -> Optional[Device]:
        """
        Find first device of specified type.
        
        Args:
            device_type: Type of device to find
            
        Returns:
            Device object if found, None otherwise
        """
        native_device = self._native.find_device(device_type.value)
        if native_device:
            return self._wrap_device(native_device)
        return None
    
    def find_devices(self, device_type: DeviceType) -> List[Device]:
        """
        Find all devices of specified type.
        
        Args:
            device_type: Type of devices to find
            
        Returns:
            List of Device objects
        """
        native_devices = self._native.find_devices(device_type.value)
        return [self._wrap_device(d) for d in native_devices]
    
    @staticmethod
    def get_version() -> str:
        """
        Get LogiLinux library version.
        
        Returns:
            Version string (e.g., "0.1.0")
        """
        version = native.Library.get_version()
        return str(version)
    
    def _wrap_device(self, native_device) -> Device:
        """Wrap native device in appropriate Python class."""
        # Check if it's an MX Keypad device
        if isinstance(native_device, native.MXKeypadDevice):
            return MXKeypadDevice(native_device)
        else:
            return Device(native_device)
