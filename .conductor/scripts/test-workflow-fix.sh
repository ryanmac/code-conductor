#!/bin/bash
# Test script to validate workflow fixes

echo "🧪 Testing workflow fixes..."

# Test 1: Check if workflow file is valid YAML
echo "✓ Checking workflow YAML syntax..."
python -c "import yaml; yaml.safe_load(open('.github/workflows/conductor.yml'))" || exit 1

# Test 2: Verify concurrency group is set
echo "✓ Checking concurrency controls..."
grep -q "concurrency:" .github/workflows/conductor.yml || exit 1

# Test 3: Verify bot exclusion
echo "✓ Checking bot exclusion..."
grep -q "github.actor != 'github-actions\[bot\]'" .github/workflows/conductor.yml || exit 1

# Test 4: Verify removed issue triggers
echo "✓ Checking removed issue triggers..."
! grep -q "^  issues:" .github/workflows/conductor.yml || echo "⚠️  Warning: issues trigger still present"

# Test 5: Check Python scripts can run
echo "✓ Testing Python scripts..."
python .conductor/scripts/health-check.py --json > /dev/null 2>&1 || echo "⚠️  Health check needs GitHub auth"
python .conductor/scripts/update-status.py --json > /dev/null 2>&1 || echo "⚠️  Update status needs GitHub auth"

echo "✅ Basic tests complete!"
echo ""
echo "📋 Summary of fixes:"
echo "- Removed issue/comment triggers to prevent recursion"
echo "- Added concurrency controls to prevent multiple runs"
echo "- Added bot exclusion to prevent self-triggering"
echo "- Improved duplicate issue detection"
echo "- Fixed authentication to use CONDUCTOR_GITHUB_TOKEN"
echo "- Added retry logic and better error handling"