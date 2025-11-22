"""
MX Keypad Example - Interactive LCD Button Display

This example demonstrates:
- Responding to all MX Keypad buttons (9 grid buttons + P1/P2 navigation)
- Rendering dynamic images to the LCD display
- Tracking button state and updating visuals in real-time

Button Layout (3x3 grid):
  [0] [1] [2]
  [3] [4] [5]
  [6] [7] [8]

Usage:
    ./run_with_lib.sh examples/keypad_example.py
"""

import time
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from logilinux import (
    Library,
    DeviceType,
    MXKeypadDevice,
    ButtonEvent,
    MXKeypadButton,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Button state tracking
button_states = {
    MXKeypadButton.GRID_0: {"count": 0, "color": (255, 100, 100)},
    MXKeypadButton.GRID_1: {"count": 0, "color": (100, 255, 100)},
    MXKeypadButton.GRID_2: {"count": 0, "color": (100, 100, 255)},
    MXKeypadButton.GRID_3: {"count": 0, "color": (255, 255, 100)},
    MXKeypadButton.GRID_4: {"count": 0, "color": (255, 100, 255)},
    MXKeypadButton.GRID_5: {"count": 0, "color": (100, 255, 255)},
    MXKeypadButton.GRID_6: {"count": 0, "color": (255, 150, 100)},
    MXKeypadButton.GRID_7: {"count": 0, "color": (150, 255, 100)},
    MXKeypadButton.GRID_8: {"count": 0, "color": (100, 150, 255)},
}

current_page = 0


def create_button_image(button: MXKeypadButton, count: int, color: tuple) -> bytes:
    """
    Create a JPEG image for a keypad button.
    
    Args:
        button: Which button this is for
        count: Number of times pressed
        color: RGB color tuple
        
    Returns:
        JPEG image data as bytes
    """
    # MX Keypad LCD buttons are 90x90 pixels
    img = Image.new('RGB', (90, 90), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw colored background
    padding = 5
    draw.rectangle(
        [padding, padding, 90-padding, 90-padding],
        fill=color,
        outline=(255, 255, 255),
        width=2
    )
    
    # Draw button number
    button_num = button.value
    num_text = str(button_num)
    
    # Draw count in center
    count_text = str(count)
    
    # Simple text positioning (no custom font)
    # Top: button number
    bbox = draw.textbbox((0, 0), num_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((45 - text_width//2, 15), num_text, fill=(255, 255, 255))
    
    # Middle: count
    bbox = draw.textbbox((0, 0), count_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((45 - text_width//2, 40), count_text, fill=(255, 255, 255))
    
    # Bottom: "PRESS"
    press_text = "PRESS"
    bbox = draw.textbbox((0, 0), press_text)
    text_width = bbox[2] - bbox[0]
    draw.text((45 - text_width//2, 65), press_text, fill=(200, 200, 200))
    
    # Convert to JPEG bytes
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def create_page_indicator_image(page: int) -> bytes:
    """Create image showing current page number."""
    img = Image.new('RGB', (90, 90), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([2, 2, 88, 88], outline=(100, 100, 255), width=3)
    
    # Draw "PAGE"
    page_text = "PAGE"
    bbox = draw.textbbox((0, 0), page_text)
    text_width = bbox[2] - bbox[0]
    draw.text((45 - text_width//2, 25), page_text, fill=(150, 150, 255))
    
    # Draw page number
    num_text = str(page)
    bbox = draw.textbbox((0, 0), num_text)
    text_width = bbox[2] - bbox[0]
    draw.text((45 - text_width//2, 50), num_text, fill=(255, 255, 255))
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def update_button_display(device: MXKeypadDevice, button_idx: int):
    """Update a specific button's LCD display."""
    button = MXKeypadButton(button_idx)
    
    logger.debug(f"update_button_display called: button_idx={button_idx}, button={button}, button.value={button.value}")
    
    if button in button_states:
        state = button_states[button]
        jpeg_data = create_button_image(button, state["count"], state["color"])
        success = device.set_key_image(button_idx, jpeg_data)
        if success:
            logger.debug(f"✓ Updated display for button {button_idx} (count={state['count']})")
        else:
            logger.warning(f"Failed to update display for button {button_idx}")


def initialize_display(device: MXKeypadDevice):
    """Initialize all button displays."""
    logger.info("Initializing MX Keypad LCD displays...")
    
    # Initialize device
    if not device.initialize():
        logger.error("Failed to initialize MX Keypad!")
        return False
    
    if not device.has_lcd():
        logger.error("Device does not have LCD support!")
        return False
    
    # Set images for all grid buttons
    for button in button_states.keys():
        update_button_display(device, button.value)
    
    logger.info("✓ All button displays initialized")
    return True


def on_event(event, device: MXKeypadDevice):
    """Handle button events from the keypad."""
    global current_page
    
    if not isinstance(event, ButtonEvent):
        return
    
    # Only respond to button presses (not releases)
    if not event.pressed:
        return
    
    button = event.get_mx_keypad_button()
    logger.info(f"Button pressed: {button.name} (code: {event.button_code})")
    
    # Handle navigation buttons (P1/P2)
    if button == MXKeypadButton.P1_LEFT:
        current_page = max(0, current_page - 1)
        logger.info(f"← Previous page: {current_page}")
        # Could update display to show page change
        
    elif button == MXKeypadButton.P2_RIGHT:
        current_page += 1
        logger.info(f"→ Next page: {current_page}")
        # Could update display to show page change
    
    # Handle grid buttons (0-8)
    elif button in button_states:
        # Increment counter
        button_states[button]["count"] += 1
        count = button_states[button]["count"]
        
        logger.info(f"Grid button {button.value} pressed {count} times")
        
        # Update the LCD display for this button
        update_button_display(device, button.value)
        
        # Special action every 5 presses
        if count % 5 == 0:
            # Cycle the color
            state = button_states[button]
            r, g, b = state["color"]
            state["color"] = (b, r, g)  # Rotate colors
            update_button_display(device, button.value)
            logger.info(f"  → Color changed to {state['color']}")
    
    else:
        logger.warning(f"Unknown button: {button}")


def main():
    """Run the MX Keypad example."""
    logger.info("=== MX Keypad LCD Example ===")
    logger.info("This demo shows:")
    logger.info("  - Press grid buttons (0-8) to increment counters")
    logger.info("  - LCD displays update in real-time")
    logger.info("  - Color changes every 5 presses")
    logger.info("  - P1/P2 buttons navigate pages")
    logger.info("")
    
    # Find MX Keypad device
    lib = Library()
    device = lib.find_device(DeviceType.MX_KEYPAD)
    
    if not device:
        logger.error("No MX Keypad found!")
        logger.error("Make sure your MX Creative Console Keypad is connected.")
        logger.error("")
        logger.error("Common issues:")
        logger.error("  1. Device not connected - plug in your MX Keypad")
        logger.error("  2. Permission denied - run with sudo or setup udev rules:")
        logger.error("     sudo ./run_with_lib.sh examples/keypad_example.py")
        logger.error("     OR")
        logger.error("     ./setup_permissions.sh  # one-time setup")
        return
    
    # Ensure it's an MXKeypadDevice
    if not isinstance(device, MXKeypadDevice):
        logger.error("Found device is not an MX Keypad!")
        return
    
    logger.info(f"✓ Found device: {device.info.name}")
    logger.info(f"  Path: {device.info.device_path}")
    logger.info(f"  Vendor ID: 0x{device.info.vendor_id:04x}")
    logger.info(f"  Product ID: 0x{device.info.product_id:04x}")
    
    # Initialize LCD displays
    if not initialize_display(device):
        return
    
    # Set up event callback
    device.set_event_callback(lambda event: on_event(event, device))
    
    # Start monitoring
    device.start_monitoring()
    logger.info("\n✓ Monitoring started. Press buttons on the keypad!")
    logger.info("  Press Ctrl+C to exit\n")
    
    # Run until interrupted
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
    finally:
        device.stop_monitoring()
        logger.info("✓ Stopped monitoring")


if __name__ == '__main__':
    main()
