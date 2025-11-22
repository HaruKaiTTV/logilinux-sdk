"""
Base classes for plugin actions.

This module provides the foundation for creating interactive actions
that respond to device inputs (buttons, dials, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum


class PluginImageSize(Enum):
    """Standard image sizes for device displays (matching C# SDK)."""
    SMALL = (50, 50)      # Small button size
    MEDIUM = (80, 80)     # Medium button size  
    LARGE = (90, 90)      # Large button size (MX Keypad LCD keys)
    
    @property
    def width(self) -> int:
        """Get width in pixels."""
        return self.value[0]
    
    @property
    def height(self) -> int:
        """Get height in pixels."""
        return self.value[1]


class PluginAction(ABC):
    """
    Base class for all plugin actions.
    
    This matches the C# SDK's action architecture but with Python idioms.
    Actions can be commands (button press) or adjustments (dial rotation).
    """
    
    def __init__(self, 
                 display_name: str,
                 description: str = "",
                 group_name: str = ""):
        """
        Initialize a plugin action.
        
        Args:
            display_name: Name shown to user in UI
            description: Description of what this action does
            group_name: Logical grouping for organization
        """
        self.display_name = display_name
        self.description = description
        self.group_name = group_name
        self._plugin: Optional[Any] = None  # Reference to parent Plugin
        self._action_parameter: str = ""    # Persistent parameter storage
    
    def set_plugin(self, plugin: Any) -> None:
        """
        Set reference to parent Plugin instance.
        
        This is called automatically by the Plugin registry.
        Allows actions to access plugin-level resources.
        """
        self._plugin = plugin
    
    @property
    def plugin(self) -> Any:
        """Get parent Plugin instance."""
        return self._plugin
    
    def get_display_name(self, action_parameter: str = "") -> str:
        """
        Get display name for this action (can be dynamic based on parameters).
        
        Args:
            action_parameter: Optional parameter string
            
        Returns:
            Display name string
        """
        return self.display_name
    
    def load(self, action_parameter: str = "") -> None:
        """
        Called when action is loaded/assigned.
        
        Override to initialize resources or parse action_parameter.
        
        Args:
            action_parameter: Serialized configuration for this action instance
        """
        self._action_parameter = action_parameter
    
    def unload(self) -> None:
        """
        Called when action is unloaded/unassigned.
        
        Override to clean up resources.
        """
        pass
    
    def action_image_changed(self, action_parameter: str = "") -> None:
        """
        Notify that action's image needs updating.
        
        This triggers get_command_image() to be called.
        In the C# SDK this is manual; we'll make it automatic via properties.
        """
        if self._plugin:
            self._plugin._notify_image_changed(self, action_parameter)
    
    def adjustment_value_changed(self, action_parameter: str = "") -> None:
        """
        Notify that adjustment's display value needs updating.
        
        This triggers get_adjustment_value() to be called.
        """
        if self._plugin:
            self._plugin._notify_value_changed(self, action_parameter)
