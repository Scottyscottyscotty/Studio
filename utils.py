"""
Utility functions for Studio
"""

import subprocess
import re
from typing import Optional


def detect_capture_one_version() -> Optional[str]:
    """
    Detect which version of Capture One is installed

    Returns:
        Version string (e.g., "23", "24") or None if not found
    """
    script = '''
    tell application "System Events"
        set appList to name of every application process whose name contains "Capture One"
        if (count of appList) > 0 then
            return item 1 of appList
        else
            return "Not Running"
        end if
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )

        app_name = result.stdout.strip()

        if app_name and app_name != "Not Running":
            # Extract version number from app name (e.g., "Capture One 23")
            match = re.search(r'Capture One (\d+)', app_name)
            if match:
                return match.group(1)

        # Try to find installed versions
        script2 = '''
        tell application "Finder"
            set appList to (name of every application file of folder "Applications" of startup disk whose name contains "Capture One")
            if (count of appList) > 0 then
                return item 1 of appList
            else
                return ""
            end if
        end tell
        '''

        result = subprocess.run(
            ['osascript', '-e', script2],
            capture_output=True,
            text=True,
            check=True
        )

        app_name = result.stdout.strip()
        match = re.search(r'Capture One (\d+)', app_name)
        if match:
            return match.group(1)

    except subprocess.CalledProcessError:
        pass

    return None


def is_capture_one_running() -> bool:
    """Check if Capture One is currently running"""
    script = '''
    tell application "System Events"
        set appList to name of every application process whose name contains "Capture One"
        return (count of appList) > 0
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip() == "true"

    except subprocess.CalledProcessError:
        return False


def launch_capture_one(version: Optional[str] = None) -> bool:
    """
    Launch Capture One

    Args:
        version: Specific version to launch (e.g., "23"). If None, launches the default.

    Returns:
        True if successful, False otherwise
    """
    app_name = f"Capture One {version}" if version else "Capture One"

    script = f'''
    tell application "{app_name}"
        activate
    end tell
    '''

    try:
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_app_name(version: Optional[str] = None) -> str:
    """
    Get the full application name for Capture One

    Args:
        version: Version number (e.g., "23")

    Returns:
        Full app name (e.g., "Capture One 23")
    """
    if version:
        return f"Capture One {version}"

    # Try to detect version
    detected_version = detect_capture_one_version()
    if detected_version:
        return f"Capture One {detected_version}"

    # Default to generic name
    return "Capture One"


if __name__ == "__main__":
    print("Capture One Detection:")
    print(f"Running: {is_capture_one_running()}")
    print(f"Version: {detect_capture_one_version()}")
    print(f"App Name: {get_app_name()}")
