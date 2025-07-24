#!/bin/bash
set -e

# Code-Conductor Agent Bootstrap Script
# This script is maintained for backward compatibility
# The preferred method is now: conductor-agent start [role]

echo "🎼 Code-Conductor Agent Bootstrap"
echo "=================================="
echo ""
echo "ℹ️  This script is deprecated. Please use the new unified command:"
echo ""
echo "    conductor-agent start [role]"
echo ""
echo "Redirecting to conductor-agent..."
echo ""

# Get the role from first argument or default
ROLE=${1:-dev}

# Execute the new conductor-agent command
exec "$(dirname "$0")/conductor-agent" start "$ROLE"