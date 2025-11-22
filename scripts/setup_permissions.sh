#!/bin/bash
# Setup udev rules for Logitech MX Creative Console devices
# This allows non-root access to the devices

echo "Setting up udev rules for Logitech MX Creative Console..."

sudo bash -c 'cat > /etc/udev/rules.d/99-logitech-creative.rules << EOF
# Logitech MX Creative Console - Dialpad (MX Dialpad)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="bc00", MODE="0666", TAG+="uaccess"

# Logitech MX Creative Console - Keypad (MX Creative Keypad)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c354", MODE="0666", TAG+="uaccess"
EOF'

echo "✓ Udev rules created"

sudo udevadm control --reload-rules
echo "✓ Udev rules reloaded"

sudo udevadm trigger
echo "✓ Devices triggered"

echo ""
echo "Done! You should now be able to access the devices without sudo."
echo "You may need to unplug and replug your devices for changes to take effect."
echo ""
echo "Test with: ./run_with_lib.sh examples/simple_monitoring.py"
