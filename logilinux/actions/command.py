"""
PluginCommand - Actions triggered by button presses.

This corresponds to PluginDynamicCommand in the C# SDK.
"""

from typing import Optional
from PIL import Image
from .base import PluginAction, PluginImageSize


class PluginCommand(PluginAction):
    """
    Command action triggered by button press.
    
    Corresponds to C# SDK's PluginDynamicCommand.
    Subclass this to create button actions for your plugin.
    
    Example:
        >>> class MuteToggle(PluginCommand):
        ...     def __init__(self):
        ...         super().__init__("Mic Toggle", "Mutes/unmutes microphone", "Audio")
        ...         self.is_muted = False
        ...     
        ...     def run_command(self, action_parameter: str = ""):
        ...         self.is_muted = not self.is_muted
        ...         # Perform actual mute action
        ...         self.action_image_changed()  # Update button image
        ...     
        ...     def get_command_image(self, action_parameter: str = "", 
        ...                          image_size: PluginImageSize = PluginImageSize.LARGE):
        ...         # Create PIL Image showing mute state
        ...         img = Image.new('RGB', (image_size.width, image_size.height))
        ...         # ... draw image ...
        ...         return img
    """
    
    def run_command(self, action_parameter: str = "") -> None:
        """
        Execute the command action.
        
        Override this method to implement your button's behavior.
        This is called when the user presses the button.
        
        Args:
            action_parameter: Configuration string for this action instance
        """
        pass
    
    def get_command_image(self,
                         action_parameter: str = "",
                         image_size: PluginImageSize = PluginImageSize.LARGE) -> Optional[Image.Image]:
        """
        Get image to display on LCD button (for MX Keypad).
        
        Override this to provide dynamic button graphics.
        Return a PIL Image object or None for no image.
        
        Args:
            action_parameter: Configuration string
            image_size: Required image dimensions
            
        Returns:
            PIL Image of specified size, or None
        """
        return None
    
    def on_button_press(self, action_parameter: str = "") -> None:
        """
        Called when button is pressed down.
        
        Override for press/release distinction.
        Default implementation calls run_command().
        """
        self.run_command(action_parameter)
    
    def on_button_release(self, action_parameter: str = "") -> None:
        """
        Called when button is released.
        
        Override if you need separate press/release handling.
        """
        pass
