"""
PluginAdjustment - Actions triggered by dial/encoder rotation.

This corresponds to PluginDynamicAdjustment in the C# SDK.
"""

from typing import Optional
from .base import PluginAction


class PluginAdjustment(PluginAction):
    """
    Adjustment action triggered by dial rotation.
    
    Corresponds to C# SDK's PluginDynamicAdjustment.
    Subclass this to create dial/encoder actions for your plugin.
    
    The dial can be both rotated (adjustment) and pressed (command).
    
    Example:
        >>> class VolumeControl(PluginAdjustment):
        ...     def __init__(self):
        ...         super().__init__("Volume", "System volume control", "Audio", has_reset=True)
        ...         self.volume = 50
        ...     
        ...     def apply_adjustment(self, action_parameter: str = "", diff: int = 0):
        ...         self.volume = max(0, min(100, self.volume + diff * 5))
        ...         # Set actual system volume
        ...         self.adjustment_value_changed()  # Update display
        ...     
        ...     def run_command(self, action_parameter: str = ""):
        ...         # Press dial to mute/unmute
        ...         pass
        ...     
        ...     def get_adjustment_value(self, action_parameter: str = "") -> str:
        ...         return f"{self.volume}%"
    """
    
    def __init__(self,
                 display_name: str,
                 description: str = "",
                 group_name: str = "",
                 has_reset: bool = False):
        """
        Initialize adjustment action.
        
        Args:
            display_name: Name shown to user
            description: Description of adjustment
            group_name: Logical grouping
            has_reset: Whether pressing the dial resets to default value
        """
        super().__init__(display_name, description, group_name)
        self.has_reset = has_reset
    
    def apply_adjustment(self, action_parameter: str = "", diff: int = 0) -> None:
        """
        Apply adjustment based on rotation.
        
        Override this method to implement dial rotation behavior.
        
        Args:
            action_parameter: Configuration string
            diff: Rotation delta (positive = clockwise, negative = counter-clockwise)
                 Magnitude depends on rotation speed (1-6 typical, higher for fast turns)
        """
        pass
    
    def run_command(self, action_parameter: str = "") -> None:
        """
        Execute command when dial is pressed.
        
        Override this for dial press behavior.
        If has_reset=True, this typically resets to default value.
        
        Args:
            action_parameter: Configuration string
        """
        pass
    
    def get_adjustment_value(self, action_parameter: str = "") -> str:
        """
        Get current value to display as on-screen overlay.
        
        Override this to show current state (e.g., "75%", "3.5x", etc.).
        This is shown in the on-screen display when user rotates dial.
        
        Args:
            action_parameter: Configuration string
            
        Returns:
            String representation of current value
        """
        return ""
    
    def on_rotation_start(self, action_parameter: str = "") -> None:
        """
        Called when user starts rotating dial.
        
        Override for rotation begin notification (e.g., show UI overlay).
        """
        pass
    
    def on_rotation_end(self, action_parameter: str = "") -> None:
        """
        Called when rotation stops.
        
        Override for rotation end notification (e.g., hide UI overlay).
        """
        pass
