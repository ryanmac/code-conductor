#!/bin/bash
set -e

# Code-Conductor Agent Bootstrap Script
# This script is maintained for backward compatibility
# The preferred method is now: ./conductor start [role]

echo "🎼 Code-Conductor Agent Bootstrap"
echo "=================================="
echo ""
echo "ℹ️  This script is deprecated. Please use the new unified command:"
echo ""
echo "    ./conductor start [role]"
echo ""
echo "Redirecting to conductor..."
echo ""

# Get the role from first argument or default
ROLE=${1:-dev}

# Execute the new conductor command
exec "$(dirname "$0")/conductor" start "$ROLE"