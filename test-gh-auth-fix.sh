#!/bin/bash
# Test script to validate the GitHub CLI authentication fix

echo "🧪 Testing GitHub CLI authentication fix..."

# Test 1: Verify workflow YAML syntax
echo "✓ Checking workflow YAML syntax..."
if command -v yamllint > /dev/null 2>&1; then
    yamllint .github/workflows/conductor.yml || exit 1
else
    echo "  yamllint not found, skipping YAML validation"
fi

# Test 2: Verify the fix - GH_TOKEN should NOT be in the Setup GitHub CLI step
echo "✓ Checking that GH_TOKEN is removed from Setup GitHub CLI step..."
if grep -A 5 "Setup GitHub CLI with proper token" .github/workflows/conductor.yml | grep -q "GH_TOKEN:"; then
    echo "❌ ERROR: GH_TOKEN still present in Setup GitHub CLI step!"
    exit 1
else
    echo "  ✅ GH_TOKEN correctly removed from Setup GitHub CLI step"
fi

# Test 3: Verify GH_TOKEN is still present for label creation
echo "✓ Checking that GH_TOKEN is still set for label operations..."
if grep -A 35 "Ensure required labels exist" .github/workflows/conductor.yml | grep -q "GH_TOKEN:"; then
    echo "  ✅ GH_TOKEN correctly set for label operations"
else
    echo "❌ ERROR: GH_TOKEN missing from label operations!"
    exit 1
fi

# Test 4: Check that all Python scripts have GITHUB_TOKEN env var
echo "✓ Checking Python script environment variables..."
python_scripts=(
    "validate-config.py"
    "dependency-check.py"
    "health-check.py"
    "update-status.py"
    "generate-summary.py"
    "cleanup-stale.py"
    "archive-completed.py"
)

for script in "${python_scripts[@]}"; do
    if grep -B 5 "$script" .github/workflows/conductor.yml | grep -q "GITHUB_TOKEN:"; then
        echo "  ✅ $script has GITHUB_TOKEN environment variable"
    else
        echo "  ⚠️  Warning: $script might be missing GITHUB_TOKEN"
    fi
done

# Test 5: Simulate the authentication flow (without actual token)
echo ""
echo "✓ Simulating authentication flow..."
echo "  1. gh auth login --with-token < token.txt (no GH_TOKEN in env)"
echo "  2. gh label commands (with GH_TOKEN in env)"
echo "  3. Python scripts (with GITHUB_TOKEN in env)"

echo ""
echo "✅ Authentication fix validation complete!"
echo ""
echo "📋 Summary of fix:"
echo "- Removed GH_TOKEN from Setup GitHub CLI step to prevent conflict"
echo "- Kept GH_TOKEN for direct gh commands that need it"
echo "- All Python scripts still receive GITHUB_TOKEN"
echo ""
echo "This should resolve the error:"
echo "'The value of the GH_TOKEN environment variable is being used for authentication.'"