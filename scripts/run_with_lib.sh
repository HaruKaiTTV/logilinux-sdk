#!/bin/bash
# Helper script to run Python with the correct library path and permissions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$SCRIPT_DIR/logilinux-driver/build/lib:$LD_LIBRARY_PATH"

# Use venv python if available, otherwise system python
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/venv/bin/python"
else
    PYTHON="python"
fi

# Check if we need sudo (hidraw devices typically require root)
if [ -w /dev/hidraw0 ] 2>/dev/null || [ -w /dev/hidraw1 ] 2>/dev/null; then
    # User has permission, run directly
    "$PYTHON" "$@"
else
    # Need sudo for hidraw access
    echo "Note: Running with sudo for device access..."
    sudo -E LD_LIBRARY_PATH="$LD_LIBRARY_PATH" "$PYTHON" "$@"
fi
