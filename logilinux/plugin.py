"""
Plugin system - Base Plugin class and registration.

This module provides the plugin lifecycle management matching the C# SDK
but with cleaner, more Pythonic patterns.
"""

from typing import Dict, List, Type, Optional, Callable
from abc import ABC
import logging

from .core import Library, Device, DeviceType
from .core.events import Event, ButtonEvent, RotationEvent
from .actions import PluginCommand, PluginAdjustment


logger = logging.getLogger(__name__)


class Plugin(ABC):
    """
    Base class for LogiLinux plugins.
    
    Corresponds to C# SDK's Plugin base class.
    Subclass this to create a plugin for Logitech devices.
    
    Lifecycle:
        1. __init__() - Plugin instantiated
        2. load() - Plugin initialized (connect to APIs, start timers, etc.)
        3. [Active execution - commands/adjustments run]
        4. unload() - Plugin cleanup (close connections, stop timers)
    
    Example:
        >>> class MyPlugin(Plugin):
        ...     def load(self):
        ...         # Initialize resources
        ...         self.api_client = MyAPIClient()
        ...         
        ...     def unload(self):
        ...         # Cleanup
        ...         self.api_client.close()
        ...         
        ...     def get_commands(self) -> List[PluginCommand]:
        ...         return [MuteCommand(), UndoCommand()]
        ...     
        ...     def get_adjustments(self) -> List[PluginAdjustment]:
        ...         return [VolumeAdjustment(), ZoomAdjustment()]
    """
    
    def __init__(self):
        """Initialize plugin instance."""
        self._loaded = False
        self._commands: Dict[str, PluginCommand] = {}
        self._adjustments: Dict[str, PluginAdjustment] = {}
        self._image_changed_callbacks: List[Callable] = []
        self._value_changed_callbacks: List[Callable] = []
    
    def load(self) -> None:
        """
        Load plugin resources.
        
        Override this to initialize:
        - API clients
        - Background timers
        - File handles
        - Network connections
        
        This is called once when the plugin is activated.
        """
        pass
    
    def unload(self) -> None:
        """
        Unload plugin and cleanup resources.
        
        Override this to cleanup:
        - Close connections
        - Stop timers
        - Release file handles
        
        This is called when plugin is deactivated or service stops.
        """
        pass
    
    def get_commands(self) -> List[PluginCommand]:
        """
        Get all commands provided by this plugin.
        
        Override to return list of PluginCommand instances.
        
        Returns:
            List of command action instances
        """
        return []
    
    def get_adjustments(self) -> List[PluginAdjustment]:
        """
        Get all adjustments provided by this plugin.
        
        Override to return list of PluginAdjustment instances.
        
        Returns:
            List of adjustment action instances
        """
        return []
    
    def _register_actions(self) -> None:
        """Internal: Register all commands and adjustments."""
        # Register commands
        for cmd in self.get_commands():
            cmd.set_plugin(self)
            cmd_name = cmd.__class__.__name__
            self._commands[cmd_name] = cmd
            logger.debug(f"Registered command: {cmd_name}")
        
        # Register adjustments
        for adj in self.get_adjustments():
            adj.set_plugin(self)
            adj_name = adj.__class__.__name__
            self._adjustments[adj_name] = adj
            logger.debug(f"Registered adjustment: {adj_name}")
    
    def _notify_image_changed(self, action: PluginCommand, action_parameter: str = "") -> None:
        """Internal: Notify that action image needs refresh."""
        for callback in self._image_changed_callbacks:
            callback(action, action_parameter)
    
    def _notify_value_changed(self, action: PluginAdjustment, action_parameter: str = "") -> None:
        """Internal: Notify that adjustment value needs refresh."""
        for callback in self._value_changed_callbacks:
            callback(action, action_parameter)
    
    def get_command(self, name: str) -> Optional[PluginCommand]:
        """Get command by class name."""
        return self._commands.get(name)
    
    def get_adjustment(self, name: str) -> Optional[PluginAdjustment]:
        """Get adjustment by class name."""
        return self._adjustments.get(name)


class PluginService:
    """
    Service that manages plugin lifecycle and device routing.
    
    This is analogous to the C# SDK's LogiPluginService but simplified.
    Handles device discovery, event routing, and plugin lifecycle.
    """
    
    def __init__(self, library: Optional[Library] = None):
        """
        Initialize plugin service.
        
        Args:
            library: LogiLinux library instance (creates new if None)
        """
        self.library = library or Library()
        self._plugins: Dict[str, Plugin] = {}
        self._device_actions: Dict[Device, Dict[int, PluginCommand]] = {}
        self._device_adjustments: Dict[Device, PluginAdjustment] = {}
        self._devices: List[Device] = []
    
    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register and load a plugin.
        
        Args:
            plugin: Plugin instance to register
        """
        plugin_name = plugin.__class__.__name__
        
        # Load plugin
        logger.info(f"Loading plugin: {plugin_name}")
        plugin.load()
        plugin._loaded = True
        
        # Register actions
        plugin._register_actions()
        
        # Store plugin
        self._plugins[plugin_name] = plugin
        logger.info(f"Plugin {plugin_name} registered successfully")
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister and unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unregister
        """
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            logger.info(f"Unloading plugin: {plugin_name}")
            plugin.unload()
            plugin._loaded = False
            del self._plugins[plugin_name]
    
    def connect_device(self, device_type: DeviceType) -> Optional[Device]:
        """
        Connect to a device and start monitoring.
        
        Args:
            device_type: Type of device to connect
            
        Returns:
            Device instance if found and connected
        """
        device = self.library.find_device(device_type)
        if device:
            device.set_event_callback(self._handle_device_event)
            device.start_monitoring()
            self._devices.append(device)
            logger.info(f"Connected to device: {device.info.name}")
            return device
        else:
            logger.warning(f"No device found of type: {device_type.name}")
            return None
    
    def assign_button_action(self, 
                            device: Device, 
                            button_code: int, 
                            command: PluginCommand) -> None:
        """
        Assign a command to a specific button.
        
        Args:
            device: Device to assign on
            button_code: Button code to assign
            command: Command action to execute on button press
        """
        if device not in self._device_actions:
            self._device_actions[device] = {}
        self._device_actions[device][button_code] = command
        logger.debug(f"Assigned {command.__class__.__name__} to button {button_code}")
    
    def assign_dial_action(self,
                          device: Device,
                          adjustment: PluginAdjustment) -> None:
        """
        Assign an adjustment to the device's dial.
        
        Args:
            device: Device to assign on
            adjustment: Adjustment action for dial rotation
        """
        self._device_adjustments[device] = adjustment
        logger.debug(f"Assigned {adjustment.__class__.__name__} to dial")
    
    def _handle_device_event(self, event: Event) -> None:
        """Internal: Route device events to appropriate actions."""
        # Find which device this event came from
        # (In a real implementation, we'd track device-to-event mapping)
        
        if isinstance(event, ButtonEvent):
            self._handle_button_event(event)
        elif isinstance(event, RotationEvent):
            self._handle_rotation_event(event)
    
    def _handle_button_event(self, event: ButtonEvent) -> None:
        """Handle button press/release events."""
        for device, actions in self._device_actions.items():
            if event.button_code in actions:
                action = actions[event.button_code]
                if event.pressed:
                    action.on_button_press()
                else:
                    action.on_button_release()
                break
    
    def _handle_rotation_event(self, event: RotationEvent) -> None:
        """Handle dial rotation events."""
        for device, adjustment in self._device_adjustments.items():
            # Route to assigned adjustment
            adjustment.apply_adjustment(diff=event.delta)
            break
    
    def shutdown(self) -> None:
        """Shutdown service and cleanup all resources."""
        # Stop all devices
        for device in self._devices:
            if device.is_monitoring:
                device.stop_monitoring()
        
        # Unload all plugins
        for plugin_name in list(self._plugins.keys()):
            self.unregister_plugin(plugin_name)
        
        logger.info("PluginService shutdown complete")
