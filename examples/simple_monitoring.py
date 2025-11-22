"""
Simple example: Basic device event monitoring.

This is the simplest possible usage of the LogiLinux SDK.
No plugins, just raw event monitoring.
"""

import time
from logilinux import Library, DeviceType

def main():
    # Create library instance
    lib = Library()
    
    print(f"LogiLinux version: {lib.get_version()}")
    
    # Find Dialpad device
    device = lib.find_device(DeviceType.DIALPAD)
    
    if not device:
        print("No Dialpad found!")
        return
    
    print(f"Found device: {device.info.name}")
    print(f"Device path: {device.info.device_path}")
    print(f"Vendor ID: 0x{device.info.vendor_id:04x}")
    print(f"Product ID: 0x{device.info.product_id:04x}")
    
    # Define event callback
    def on_event(event):
        from logilinux import RotationEvent, ButtonEvent
        
        if isinstance(event, RotationEvent):
            direction = "clockwise" if event.delta > 0 else "counter-clockwise"
            print(f"Dial rotated {direction}: delta={event.delta}, high_res={event.delta_high_res}")
        
        elif isinstance(event, ButtonEvent):
            button = event.get_dialpad_button()
            status = "pressed" if event.pressed else "released"
            print(f"Button {button.name} {status}")
    
    # Set callback and start monitoring
    device.set_event_callback(on_event)
    device.start_monitoring()
    
    print("\nMonitoring device events. Press Ctrl+C to exit...")
    print("Try rotating the dial or pressing buttons!\n")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        device.stop_monitoring()

if __name__ == '__main__':
    main()
