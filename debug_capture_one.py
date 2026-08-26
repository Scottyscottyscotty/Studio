#!/usr/bin/env python3
"""
Debug script to test Capture One integration
"""

import subprocess
from utils import detect_capture_one_version, get_app_name, is_capture_one_running

print("=" * 60)
print("CAPTURE ONE DEBUG SCRIPT")
print("=" * 60)

# Test 1: Check if Capture One is running
print("\n1. Checking if Capture One is running...")
is_running = is_capture_one_running()
print(f"   Result: {is_running}")

# Test 2: Detect version
print("\n2. Detecting Capture One version...")
version = detect_capture_one_version()
print(f"   Detected version: {version}")

# Test 3: Get app name
print("\n3. Getting app name...")
app_name = get_app_name(version)
print(f"   App name: {app_name}")

# Test 4: List running applications
print("\n4. Listing running applications with 'Capture' in name...")
result = subprocess.run(
    ["osascript", "-e", 'tell application "System Events" to get name of every process whose name contains "Capture"'],
    capture_output=True,
    text=True
)
print(f"   Output: {result.stdout.strip()}")
if result.stderr:
    print(f"   Error: {result.stderr.strip()}")

# Test 5: Try to activate Capture One
print(f"\n5. Trying to activate '{app_name}'...")
script = f'tell application "{app_name}" to activate'
result = subprocess.run(
    ["osascript", "-e", script],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("   ✓ Successfully activated!")
else:
    print(f"   ✗ Failed: {result.stderr.strip()}")

# Test 6: Try to press "3" key
print(f"\n6. Testing keyboard shortcut (pressing '3' for 3-star rating)...")
script = f'''
tell application "{app_name}"
    activate
end tell

delay 0.2

tell application "System Events"
    tell process "{app_name}"
        keystroke "3"
    end tell
end tell
'''
result = subprocess.run(
    ["osascript", "-e", script],
    capture_output=True,
    text=True,
    timeout=5
)
if result.returncode == 0:
    print("   ✓ Keystroke sent! Check if image got 3 stars in Capture One.")
else:
    print(f"   ✗ Failed: {result.stderr.strip()}")

# Test 7: Check accessibility permissions
print("\n7. Checking System Events permissions...")
script = '''
tell application "System Events"
    set frontApp to name of first process whose frontmost is true
    return frontApp
end tell
'''
result = subprocess.run(
    ["osascript", "-e", script],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print(f"   ✓ System Events can access processes")
    print(f"   Current frontmost app: {result.stdout.strip()}")
else:
    print(f"   ✗ System Events access denied - check System Preferences > Privacy > Accessibility")
    print(f"   Error: {result.stderr.strip()}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nIf Test 6 worked (image got 3 stars), the problem is with")
print("command parsing. If Test 6 failed, the problem is with")
print("AppleScript/Accessibility permissions.")
print("\nTo fix permissions:")
print("1. Open System Preferences > Security & Privacy > Privacy")
print("2. Click 'Accessibility' on the left")
print("3. Make sure Terminal (or Python) is in the list and checked")
print("=" * 60)
