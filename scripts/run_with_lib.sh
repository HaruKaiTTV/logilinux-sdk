#!/bin/bash
# Helper script to run Python with the correct library path and permissions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export LD_LIBRARY_PATH="$PROJECT_ROOT/logilinux-driver/build/lib:$LD_LIBRARY_PATH"

# Use venv python if available, otherwise system python
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
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
