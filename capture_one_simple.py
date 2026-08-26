"""
Simplified Capture One Controller
Clean, readable, scalable
"""

import subprocess
from typing import Optional


class CaptureOneController:
    """Execute commands in Capture One via AppleScript"""

    def __init__(self, app_name: str = "Capture One"):
        self.app_name = app_name

    def execute(self, command: dict) -> bool:
        """
        Execute a parsed command

        Args:
            command: Dict with action, target, value, etc.

        Returns:
            True if successful
        """
        action = command.get('action')
        target = command.get('target', 'selected')
        value = command.get('value')
        color = command.get('color')
        direction = command.get('direction')

        print(f"[DEBUG] Executing: {action} on {target} (value={value}, color={color})")

        # Route to appropriate handler
        if action == 'rate':
            return self.rate(target, value)
        elif action == 'label':
            return self.label(target, color)
        elif action == 'delete':
            return self.delete(target, value)
        elif action == 'flag':
            return self.flag(target)
        elif action == 'reject':
            return self.reject(target)
        elif action == 'select':
            return self.select(target, value)
        elif action == 'export':
            return self.export(target)
        elif action == 'navigate':
            return self.navigate(target)
        elif action == 'rotate':
            return self.rotate(direction)
        elif action == 'flip':
            return self.flip(direction)
        elif action == 'zoom':
            return self.zoom(value)
        elif action == 'auto_adjust':
            return self.keystroke('a')  # Auto-adjust
        elif action == 'reset':
            return self.keystroke('command+shift+r')  # Reset adjustments
        elif action == 'copy_adjustments':
            return self.keystroke('command+shift+c')
        elif action == 'paste_adjustments':
            return self.keystroke('command+shift+v')
        else:
            print(f"[ERROR] Unknown action: {action}")
            return False

    # ============================================================
    # CORE ACTIONS - Clean and simple
    # ============================================================

    def rate(self, target: str, rating: int) -> bool:
        """Rate image(s) 1-5 stars"""
        if not rating or rating < 1 or rating > 5:
            return False

        if target == 'selected':
            return self.keystroke(str(rating))
        else:
            # For 'last', 'first', etc., select then rate
            if self.select(target, 1):
                return self.keystroke(str(rating))
            return False

    def label(self, target: str, color: str) -> bool:
        """Apply color label"""
        color_keys = {
            'red': 'command+1',
            'orange': 'command+2',
            'yellow': 'command+3',
            'green': 'command+4',
            'blue': 'command+5',
            'purple': 'command+6',
            'white': 'command+7'
        }

        if color not in color_keys:
            return False

        if target == 'selected':
            return self.keystroke(color_keys[color])
        else:
            if self.select(target, 1):
                return self.keystroke(color_keys[color])
            return False

    def delete(self, target: str, count: Optional[int] = 1) -> bool:
        """Delete image(s)"""
        if target == 'selected':
            return self.keystroke('delete')
        elif target == 'last':
            if self.navigate('last'):
                return self.keystroke('delete')
        return False

    def flag(self, target: str) -> bool:
        """Flag image(s)"""
        if target == 'selected':
            return self.keystroke('/')
        elif target == 'last':
            if self.navigate('last'):
                return self.keystroke('/')
        return False

    def reject(self, target: str) -> bool:
        """Reject image(s)"""
        if target == 'selected':
            return self.keystroke('command+delete')
        return False

    def select(self, target: str, count: Optional[int] = 1) -> bool:
        """Select image(s)"""
        if target == 'all':
            return self.keystroke('command+a')
        elif target == 'last':
            return self.navigate('last')
        elif target == 'first':
            return self.navigate('first')
        return True

    def export(self, target: str) -> bool:
        """Export image(s)"""
        if target == 'selected':
            return self.keystroke('command+shift+e')
        elif target == 'all':
            if self.keystroke('command+a'):  # Select all
                return self.keystroke('command+shift+e')
        return False

    def navigate(self, direction: str) -> bool:
        """Navigate between images"""
        nav_keys = {
            'next': 'right',
            'previous': 'left',
            'first': 'home',
            'last': 'end'
        }

        key = nav_keys.get(direction)
        if key:
            return self.keystroke(key)
        return False

    def rotate(self, direction: str) -> bool:
        """Rotate image"""
        if direction == 'left':
            return self.keystroke('l')
        elif direction == 'right':
            return self.keystroke('r')
        return False

    def flip(self, direction: str) -> bool:
        """Flip image"""
        if direction == 'horizontal':
            return self.keystroke('h')
        elif direction == 'vertical':
            return self.keystroke('v')
        return False

    def zoom(self, level: Optional[int]) -> bool:
        """Zoom control"""
        if level == 100:
            return self.keystroke('command+0')  # 100%
        elif level == 0:
            return self.keystroke('z')  # Fit
        return False

    # ============================================================
    # LOW-LEVEL APPLESCRIPT EXECUTION
    # ============================================================

    def keystroke(self, keys: str) -> bool:
        """
        Send keystroke to Capture One

        Args:
            keys: Key to press (e.g. "3", "command+a", "delete")

        Returns:
            True if successful
        """
        # Parse key combination
        modifiers = []
        key = keys

        if 'command+' in keys:
            modifiers.append('command down')
            key = keys.split('+')[-1]
        if 'shift+' in keys:
            modifiers.append('shift down')
            key = keys.split('+')[-1]
        if 'option+' in keys:
            modifiers.append('option down')
            key = keys.split('+')[-1]

        # Build keystroke command
        if modifiers:
            keystroke_cmd = f"{' & '.join(modifiers)} & {key} & {' & '.join([m.replace('down', 'up') for m in modifiers])}"
        else:
            keystroke_cmd = f'"{key}"'

        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                keystroke {keystroke_cmd}
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _run_applescript(self, script: str) -> bool:
        """Execute AppleScript and return success status"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] AppleScript failed: {e}")
            return False
