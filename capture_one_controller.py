"""
Capture One Controller
Executes commands in Capture One Pro using AppleScript and keyboard shortcuts
"""

import subprocess
from typing import Dict, Any
from command_parser import Command
from utils import detect_capture_one_version, get_app_name, is_capture_one_running


class CaptureOneController:
    """Controls Capture One Pro through AppleScript"""

    def __init__(self):
        # Detect Capture One version
        self.version = detect_capture_one_version()
        self.app_name = get_app_name(self.version)
        # Keyboard shortcuts for common actions
        # These match default Capture One shortcuts
        self.shortcuts = {
            'delete': 'delete',
            'next_image': 'right arrow',
            'previous_image': 'left arrow',
            'select_all': 'command down & a & command up',
            'deselect_all': 'escape',
            'export': 'command down & shift down & e & shift up & command up',
            'flag': 'slash',
            'unflag': 'slash',
            'reject': 'command down & delete & command up',
            'crop_enable': 'c',
            'crop_apply': 'return',
            'crop_cancel': 'escape',
            'reset_all': 'command down & shift down & r & shift up & command up',
        }

        # Star ratings keyboard shortcuts (1-5)
        self.rating_shortcuts = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5'
        }

        # Color label shortcuts
        self.color_shortcuts = {
            'red': 'command down & 1 & command up',
            'orange': 'command down & 2 & command up',
            'yellow': 'command down & 3 & command up',
            'green': 'command down & 4 & command up',
            'blue': 'command down & 5 & command up',
            'purple': 'command down & 6 & command up',
            'white': 'command down & 7 & command up',
        }

    def execute(self, command: Command) -> bool:
        """
        Execute a command in Capture One

        Args:
            command: The Command object to execute

        Returns:
            True if successful, False otherwise
        """
        try:
            # Route to the appropriate handler based on action
            if command.action == 'delete_last':
                return self._delete_last(command.params.get('count', 1))
            elif command.action == 'delete_selected':
                return self._delete_selected()
            elif command.action == 'rate_last':
                return self._rate_last(
                    command.params.get('count', 1),
                    command.params.get('rating')
                )
            elif command.action == 'rate_selected':
                return self._rate_selected(command.params.get('rating'))
            elif command.action == 'label_last':
                return self._label_last(
                    command.params.get('count', 1),
                    command.params.get('color')
                )
            elif command.action == 'label_selected':
                return self._label_selected(command.params.get('color'))
            elif command.action == 'select_by_color':
                return self._select_by_color(command.params.get('color'))
            elif command.action == 'select_by_rating':
                return self._select_by_rating(command.params.get('rating'))
            elif command.action == 'select_last':
                return self._select_last(command.params.get('count'))
            elif command.action == 'select_all':
                return self._press_shortcut('select_all')
            elif command.action == 'deselect_all':
                return self._press_shortcut('deselect_all')
            elif command.action == 'export_selected':
                return self._press_shortcut('export')
            elif command.action == 'export_last':
                return self._export_last(command.params.get('count'))
            elif command.action == 'adjust_exposure':
                return self._adjust_exposure(command.params.get('amount'))
            elif command.action == 'reset_adjustments':
                return self._press_shortcut('reset_all')
            elif command.action == 'next_image':
                return self._press_shortcut('next_image')
            elif command.action == 'previous_image':
                return self._press_shortcut('previous_image')
            elif command.action == 'flag_selected':
                return self._press_shortcut('flag')
            elif command.action == 'unflag_selected':
                return self._press_shortcut('unflag')
            elif command.action == 'reject_selected':
                return self._press_shortcut('reject')
            elif command.action == 'enable_crop':
                return self._press_shortcut('crop_enable')
            elif command.action == 'disable_crop':
                return self._press_shortcut('crop_cancel')
            elif command.action == 'apply_crop':
                return self._press_shortcut('crop_apply')
            else:
                print(f"Unknown action: {command.action}")
                return False

        except Exception as e:
            print(f"Error executing command: {e}")
            return False

    def _run_applescript(self, script: str) -> bool:
        """Execute an AppleScript command"""
        try:
            subprocess.run(
                ['osascript', '-e', script],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e.stderr}")
            return False

    def _press_shortcut(self, shortcut_name: str, delay: float = 0.1) -> bool:
        """Press a keyboard shortcut in Capture One"""
        if shortcut_name not in self.shortcuts:
            return False

        keystroke = self.shortcuts[shortcut_name]

        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay {delay}

        tell application "System Events"
            tell process "{self.app_name}"
                keystroke {keystroke}
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _press_key(self, keystroke: str, delay: float = 0.1) -> bool:
        """Press a specific key combination in Capture One"""
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay {delay}

        tell application "System Events"
            tell process "{self.app_name}"
                keystroke {keystroke}
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _delete_selected(self) -> bool:
        """Delete the currently selected image(s)"""
        return self._press_shortcut('delete')

    def _delete_last(self, count: int) -> bool:
        """Delete the last N images"""
        # Navigate to the last image and select backwards
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Go to last image
                key code 119  -- End key
                delay 0.1

                -- Select last N images
                repeat {count - 1} times
                    keystroke (up arrow) using shift down
                    delay 0.05
                end repeat

                delay 0.1

                -- Delete
                keystroke delete
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _rate_selected(self, rating: int) -> bool:
        """Rate the currently selected image(s)"""
        if rating not in self.rating_shortcuts:
            return False

        keystroke = self.rating_shortcuts[rating]
        return self._press_key(keystroke)

    def _rate_last(self, count: int, rating: int) -> bool:
        """Rate the last N images"""
        if rating not in self.rating_shortcuts:
            return False

        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Go to last image
                key code 119  -- End key
                delay 0.1

                -- Select last N images
                repeat {count - 1} times
                    keystroke (up arrow) using shift down
                    delay 0.05
                end repeat

                delay 0.1

                -- Apply rating
                keystroke "{self.rating_shortcuts[rating]}"
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _label_selected(self, color: str) -> bool:
        """Apply a color label to selected image(s)"""
        if color not in self.color_shortcuts:
            return False

        keystroke = self.color_shortcuts[color]
        return self._press_key(keystroke)

    def _label_last(self, count: int, color: str) -> bool:
        """Apply a color label to the last N images"""
        if color not in self.color_shortcuts:
            return False

        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Go to last image
                key code 119  -- End key
                delay 0.1

                -- Select last N images
                repeat {count - 1} times
                    keystroke (up arrow) using shift down
                    delay 0.05
                end repeat

                delay 0.1

                -- Apply color label
                keystroke {self.color_shortcuts[color]}
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _select_last(self, count: int) -> bool:
        """Select the last N images"""
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Go to last image
                key code 119  -- End key
                delay 0.1

                -- Select last N images
                repeat {count - 1} times
                    keystroke (up arrow) using shift down
                    delay 0.05
                end repeat
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _select_by_color(self, color: str) -> bool:
        """Select all images with a specific color label"""
        # This requires using Capture One's filter functionality
        # We'll use the Filter tool and keyboard navigation
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.2

        tell application "System Events"
            tell process "{self.app_name}"
                -- Open filter panel (Command + Option + F)
                keystroke "f" using {{command down, option down}}
                delay 0.3

                -- This is a simplified version
                -- In practice, you'd need to navigate the filter UI
                -- For now, we'll just note this needs manual implementation
            end tell
        end tell
        '''

        # Note: This is a placeholder. Full implementation would require
        # GUI scripting to navigate Capture One's filter interface
        print(f"Filter by color not fully implemented yet. Color: {color}")
        return True

    def _select_by_rating(self, rating: int) -> bool:
        """Select all images with a specific rating"""
        # Similar to color filtering, this requires filter panel navigation
        print(f"Filter by rating not fully implemented yet. Rating: {rating}")
        return True

    def _export_last(self, count: int) -> bool:
        """Export the last N images"""
        # Select the last N images, then export
        if self._select_last(count):
            return self._press_shortcut('export')
        return False

    def _adjust_exposure(self, amount: int) -> bool:
        """Adjust exposure by a specific amount"""
        # Navigate to exposure slider and adjust
        # This is a simplified version - actual implementation would
        # need to navigate to the exposure control
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- This is a placeholder
                -- Full implementation would navigate to exposure slider
                -- and adjust by the specified amount
            end tell
        end tell
        '''

        print(f"Exposure adjustment not fully implemented yet. Amount: {amount}")
        return True


# Test function
if __name__ == "__main__":
    from command_parser import CommandParser

    controller = CaptureOneController()
    parser = CommandParser()

    # Test command
    test_text = "Studio, rate the last image as 5 stars"
    command = parser.parse(test_text)

    if command:
        print(f"Executing: {command}")
        success = controller.execute(command)
        print(f"Success: {success}")
    else:
        print("Command not recognized")
