"""
Example Plugin demonstrating LogiLinux SDK usage.

This example shows how to create a plugin with commands and adjustments
for the MX Creative Console (Dialpad + Keypad).

Usage:
    python examples/example_plugin.py
"""

import time
import logging
from PIL import Image, ImageDraw, ImageFont

from logilinux import (
    Plugin,
    PluginService,
    PluginCommand,
    PluginAdjustment,
    PluginImageSize,
    DeviceType,
    MXKeypadButton,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MuteToggleCommand(PluginCommand):
    """
    Example command: Toggle microphone mute with visual feedback.
    
    Matches C# SDK pattern but with Python simplicity.
    """
    
    def __init__(self):
        super().__init__(
            display_name="Mic Toggle",
            description="Mute/unmute microphone",
            group_name="Audio"
        )
        self._is_muted = False
    
    def run_command(self, action_parameter: str = ""):
        """Execute the mute toggle."""
        self._is_muted = not self._is_muted
        logger.info(f"Microphone {'MUTED' if self._is_muted else 'UNMUTED'}")
        
        # In real implementation, call OS mute API here
        # Example: subprocess.run(['pactl', 'set-source-mute', '@DEFAULT_SOURCE@', 'toggle'])
        
        # Notify that button image should update
        self.action_image_changed(action_parameter)
    
    def get_command_image(self, 
                         action_parameter: str = "",
                         image_size: PluginImageSize = PluginImageSize.LARGE) -> Image.Image:
        """Generate dynamic button image based on mute state."""
        # Create image
        img = Image.new('RGB', (image_size.width, image_size.height))
        draw = ImageDraw.Draw(img)
        
        # Draw background
        bg_color = (200, 0, 0) if self._is_muted else (0, 200, 0)
        draw.rectangle([0, 0, image_size.width, image_size.height], fill=bg_color)
        
        # Draw text
        text = "MUTED" if self._is_muted else "LIVE"
        text_color = (255, 255, 255) if self._is_muted else (0, 0, 0)
        
        # Simple centered text (no font for simplicity)
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((image_size.width - text_width) // 2, 
                   (image_size.height - text_height) // 2)
        draw.text(position, text, fill=text_color)
        
        return img


class VolumeAdjustment(PluginAdjustment):
    """
    Example adjustment: Volume control with dial.
    
    Rotate to adjust, press to mute/unmute.
    """
    
    def __init__(self):
        super().__init__(
            display_name="Volume",
            description="System volume control",
            group_name="Audio",
            has_reset=True
        )
        self._volume = 50  # 0-100
    
    def apply_adjustment(self, action_parameter: str = "", diff: int = 0):
        """Apply volume change based on dial rotation."""
        # Each tick adjusts by 5%
        self._volume = max(0, min(100, self._volume + diff * 5))
        
        logger.info(f"Volume: {self._volume}%")
        
        # In real implementation, set system volume here
        # Example: subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{self._volume}%'])
        
        # Notify that display value should update
        self.adjustment_value_changed(action_parameter)
    
    def run_command(self, action_parameter: str = ""):
        """Reset volume to 50% when dial is pressed."""
        if self.has_reset:
            self._volume = 50
            logger.info("Volume reset to 50%")
            self.adjustment_value_changed(action_parameter)
    
    def get_adjustment_value(self, action_parameter: str = "") -> str:
        """Return current volume as displayable string."""
        return f"{self._volume}%"


class UndoCommand(PluginCommand):
    """Simple command: Send Ctrl+Z."""
    
    def __init__(self):
        super().__init__(
            display_name="Undo",
            description="Undo last action",
            group_name="Edit"
        )
    
    def run_command(self, action_parameter: str = ""):
        """Send Ctrl+Z keyboard shortcut."""
        logger.info("Undo triggered")
        # In real implementation, send keyboard event
        # Example: from pynput.keyboard import Controller, Key
        # keyboard = Controller()
        # with keyboard.pressed(Key.ctrl):
        #     keyboard.press('z')
        #     keyboard.release('z')


class ZoomAdjustment(PluginAdjustment):
    """Example adjustment: Zoom control."""
    
    def __init__(self):
        super().__init__(
            display_name="Zoom",
            description="Zoom in/out",
            group_name="View",
            has_reset=True
        )
        self._zoom = 100  # percentage
    
    def apply_adjustment(self, action_parameter: str = "", diff: int = 0):
        """Adjust zoom level."""
        self._zoom = max(10, min(400, self._zoom + diff * 10))
        logger.info(f"Zoom: {self._zoom}%")
        self.adjustment_value_changed(action_parameter)
    
    def run_command(self, action_parameter: str = ""):
        """Reset zoom to 100%."""
        self._zoom = 100
        logger.info("Zoom reset to 100%")
        self.adjustment_value_changed(action_parameter)
    
    def get_adjustment_value(self, action_parameter: str = "") -> str:
        return f"{self._zoom}%"


class ExamplePlugin(Plugin):
    """
    Example plugin demonstrating the LogiLinux SDK.
    
    Provides commands for buttons and adjustments for dials.
    """
    
    def load(self):
        """Initialize plugin resources."""
        logger.info("ExamplePlugin loading...")
        # Initialize any API clients, timers, etc. here
    
    def unload(self):
        """Cleanup plugin resources."""
        logger.info("ExamplePlugin unloading...")
        # Close connections, stop timers, etc. here
    
    def get_commands(self):
        """Return all command actions."""
        return [
            MuteToggleCommand(),
            UndoCommand(),
        ]
    
    def get_adjustments(self):
        """Return all adjustment actions."""
        return [
            VolumeAdjustment(),
            ZoomAdjustment(),
        ]


def main():
    """Run example plugin with MX Creative Console."""
    logger.info("Starting ExamplePlugin demo...")
    
    # Create plugin service
    service = PluginService()
    
    # Register our plugin
    plugin = ExamplePlugin()
    service.register_plugin(plugin)
    
    # Connect to devices
    keypad = service.connect_device(DeviceType.MX_KEYPAD)
    dialpad = service.connect_device(DeviceType.DIALPAD)
    
    if not keypad and not dialpad:
        logger.error("No devices found!")
        return
    
    # Assign actions to buttons/dials
    if keypad:
        # Get the commands from plugin
        mute_cmd = plugin.get_command('MuteToggleCommand')
        undo_cmd = plugin.get_command('UndoCommand')
        
        # Assign to keypad buttons
        if mute_cmd:
            service.assign_button_action(keypad, MXKeypadButton.GRID_0.value, mute_cmd)
        if undo_cmd:
            service.assign_button_action(keypad, MXKeypadButton.GRID_1.value, undo_cmd)
    
    if dialpad:
        # Get adjustment
        volume_adj = plugin.get_adjustment('VolumeAdjustment')
        if volume_adj:
            service.assign_dial_action(dialpad, volume_adj)
    
    logger.info("Plugin running. Press Ctrl+C to exit.")
    logger.info("Try pressing buttons or rotating the dial!")
    
    # Run until interrupted
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        service.shutdown()


if __name__ == '__main__':
    main()
