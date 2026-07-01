#!/bin/bash
# Studio v2.1 Upgrade Test Script
# Run this before deploying to verify everything works

set -e

echo "🧪 Studio v2.1 Upgrade Test Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Track test results
FAILURES=0

echo "Step 1: Environment Check"
echo "--------------------------"

# Check Python version
if python3 --version | grep -q "Python 3\.[9-9]\|Python 3\.1[0-9]"; then
    print_status 0 "Python 3.9+ detected"
else
    print_status 1 "Python 3.9+ required (you have: $(python3 --version))"
    FAILURES=$((FAILURES + 1))
fi

# Check PortAudio
if brew list portaudio &>/dev/null; then
    print_status 0 "PortAudio installed"
else
    print_status 1 "PortAudio not found (run: brew install portaudio)"
    FAILURES=$((FAILURES + 1))
fi

# Check .env file
if [ -f .env ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        print_status 0 ".env file exists with API key"
    else
        print_status 1 ".env file exists but API key looks invalid"
        FAILURES=$((FAILURES + 1))
    fi
else
    print_status 1 ".env file not found (copy from .env.example)"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "Step 2: Backup Current Environment"
echo "-----------------------------------"

# Backup current requirements
if pip freeze > old_requirements.backup.txt; then
    print_status 0 "Backed up current packages to old_requirements.backup.txt"
else
    print_status 1 "Failed to backup packages"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "Step 3: Dependency Installation"
echo "--------------------------------"

# Ask user if they want to proceed with installation
read -p "Install updated dependencies? This will upgrade openai to 2.41.0+ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Uninstall old versions
    echo "Uninstalling old versions..."
    pip uninstall openai httpx -y &>/dev/null || true

    # Install new versions
    echo "Installing new versions..."
    if pip install -r requirements.txt; then
        print_status 0 "Dependencies installed successfully"
    else
        print_status 1 "Failed to install dependencies"
        echo ""
        echo "To rollback:"
        echo "  pip install -r old_requirements.backup.txt"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping installation. You can install later with:"
    echo "  pip install --upgrade -r requirements.txt"
fi

echo ""
echo "Step 4: Verify Installed Versions"
echo "----------------------------------"

# Check openai version
OPENAI_VERSION=$(pip show openai 2>/dev/null | grep "Version:" | cut -d' ' -f2)
if [ ! -z "$OPENAI_VERSION" ]; then
    if printf '%s\n' "2.41.0" "$OPENAI_VERSION" | sort -V -C; then
        print_status 0 "openai $OPENAI_VERSION (>= 2.41.0 ✓)"
    else
        print_status 1 "openai $OPENAI_VERSION (expected >= 2.41.0)"
        FAILURES=$((FAILURES + 1))
    fi
else
    print_status 1 "openai package not found"
    FAILURES=$((FAILURES + 1))
fi

# Check pynput version
PYNPUT_VERSION=$(pip show pynput 2>/dev/null | grep "Version:" | cut -d' ' -f2)
if [ ! -z "$PYNPUT_VERSION" ]; then
    print_status 0 "pynput $PYNPUT_VERSION"
else
    print_status 1 "pynput package not found"
    FAILURES=$((FAILURES + 1))
fi

# Check pyaudio
PYAUDIO_VERSION=$(pip show pyaudio 2>/dev/null | grep "Version:" | cut -d' ' -f2)
if [ ! -z "$PYAUDIO_VERSION" ]; then
    print_status 0 "pyaudio $PYAUDIO_VERSION"
else
    print_status 1 "pyaudio package not found"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "Step 5: Import Test"
echo "-------------------"

# Test if we can import the modules
python3 -c "
import sys
try:
    from openai import OpenAI
    print('✓ OpenAI module imports successfully')
except ImportError as e:
    print(f'✗ Failed to import OpenAI: {e}')
    sys.exit(1)

try:
    import pyaudio
    print('✓ pyaudio module imports successfully')
except ImportError as e:
    print(f'✗ Failed to import pyaudio: {e}')
    sys.exit(1)

try:
    import rumps
    print('✓ rumps module imports successfully')
except ImportError as e:
    print(f'✗ Failed to import rumps: {e}')
    sys.exit(1)
" || FAILURES=$((FAILURES + 1))

echo ""
echo "Step 6: Configuration Test"
echo "--------------------------"

# Test if studio.py can be imported
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    # Just test if the file can be parsed and Config class defined
    with open('studio.py', 'r') as f:
        code = f.read()

    # Check for Config class
    if 'class Config:' in code:
        print('✓ Config class found in studio.py')
    else:
        print('✗ Config class not found in studio.py')
        sys.exit(1)

    # Check version
    if 'VERSION = \"2.1\"' in code:
        print('✓ Version 2.1 confirmed')
    else:
        print('⚠ Version string not found or incorrect')

except Exception as e:
    print(f'✗ Error reading studio.py: {e}')
    sys.exit(1)
" || FAILURES=$((FAILURES + 1))

echo ""
echo "=================================="
echo "📊 Test Summary"
echo "=================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "You're ready to run Studio v2.1:"
    echo "  python3 studio.py"
    echo ""
    echo "⚠️  IMPORTANT: Test the following manually:"
    echo "  1. Say a voice command and verify it transcribes"
    echo "  2. Confirm you hear OpenAI TTS (nova voice), NOT Mac Samantha"
    echo "  3. Check that 5-second timeout is comfortable"
    echo "  4. Try at least 10 different commands"
    echo ""
    echo "If anything breaks, rollback with:"
    echo "  git checkout 8af2268"
    echo "  pip install -r old_requirements.backup.txt"
else
    echo -e "${RED}❌ $FAILURES TEST(S) FAILED${NC}"
    echo ""
    echo "Fix the issues above before running Studio."
    echo ""
    echo "To rollback:"
    echo "  pip install -r old_requirements.backup.txt"
    exit 1
fi
