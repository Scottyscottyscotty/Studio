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
            # Basic operations
            'delete': 'delete',
            'next_image': 'right arrow',
            'previous_image': 'left arrow',
            'first_image': 'home',
            'last_image': 'end',

            # Selection
            'select_all': 'command down & a & command up',
            'deselect_all': 'escape',

            # Export
            'export': 'command down & shift down & e & shift up & command up',

            # Flag/Reject
            'flag': 'slash',
            'unflag': 'slash',
            'reject': 'command down & delete & command up',

            # Crop
            'crop_enable': 'c',
            'crop_apply': 'return',
            'crop_cancel': 'escape',
            'reset_crop': 'command down & z & command up',  # Undo after entering crop

            # Rotation
            'rotate_left': 'l',
            'rotate_right': 'r',

            # Adjustments
            'reset_all': 'command down & shift down & r & shift up & command up',
            'auto_adjust': 'command down & d & command up',

            # Copy/Paste
            'copy_adjustments': 'command down & shift down & c & shift up & command up',
            'paste_adjustments': 'command down & shift down & v & shift up & command up',

            # View
            'fullscreen': 'f',
            'zoom_to_fit': 'command down & 0 & command up',
            'zoom_100': 'command down & option down & 0 & option up & command up',
            'zoom_in': 'command down & plus & command up',
            'zoom_out': 'command down & minus & command up',

            # Comparison
            'compare': 'option down & return & option up',
            'before_after': 'b',

            # Focus
            'focus_mask': 'command down & shift down & f & shift up & command up',
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
            action = command.action

            # Delete commands
            if action == 'delete_last':
                return self._delete_last(command.params.get('count', 1))
            elif action == 'delete_selected':
                return self._delete_selected()

            # Rating commands
            elif action == 'rate_last':
                return self._rate_last(
                    command.params.get('count', 1),
                    command.params.get('rating')
                )
            elif action == 'rate_selected':
                return self._rate_selected(command.params.get('rating'))

            # Label commands
            elif action == 'label_last':
                return self._label_last(
                    command.params.get('count', 1),
                    command.params.get('color')
                )
            elif action == 'label_selected':
                return self._label_selected(command.params.get('color'))
            elif action == 'remove_label':
                return self._remove_label()

            # Selection commands
            elif action == 'select_by_color':
                return self._select_by_color(command.params.get('color'))
            elif action == 'select_by_rating':
                return self._select_by_rating(command.params.get('rating'))
            elif action == 'select_last':
                return self._select_last(command.params.get('count'))
            elif action == 'select_first':
                return self._select_first(command.params.get('count'))
            elif action == 'select_all':
                return self._press_shortcut('select_all')
            elif action == 'deselect_all':
                return self._press_shortcut('deselect_all')
            elif action == 'select_flagged':
                return self._select_flagged()
            elif action == 'select_rejected':
                return self._select_rejected()

            # Export commands
            elif action == 'export_selected':
                return self._press_shortcut('export')
            elif action == 'export_last':
                return self._export_last(command.params.get('count'))
            elif action == 'export_all':
                return self._export_all()

            # Adjustment commands
            elif action == 'adjust_exposure':
                return self._adjust_exposure(command.params.get('amount'))
            elif action == 'adjust_contrast':
                return self._adjust_contrast(command.params.get('amount'))
            elif action == 'adjust_saturation':
                return self._adjust_saturation(command.params.get('amount'))
            elif action == 'auto_adjust':
                return self._press_shortcut('auto_adjust')
            elif action == 'reset_adjustments':
                return self._press_shortcut('reset_all')

            # Navigation commands
            elif action == 'next_image':
                return self._press_shortcut('next_image')
            elif action == 'previous_image':
                return self._press_shortcut('previous_image')
            elif action == 'first_image':
                return self._press_shortcut('first_image')
            elif action == 'last_image':
                return self._press_shortcut('last_image')

            # Flag commands
            elif action == 'flag_selected':
                return self._press_shortcut('flag')
            elif action == 'unflag_selected':
                return self._press_shortcut('unflag')
            elif action == 'flag_last':
                return self._flag_last(command.params.get('count'))

            # Reject commands
            elif action == 'reject_selected':
                return self._press_shortcut('reject')
            elif action == 'unreject_selected':
                return self._unreject_selected()

            # Crop commands
            elif action == 'enable_crop':
                return self._press_shortcut('crop_enable')
            elif action == 'disable_crop':
                return self._press_shortcut('crop_cancel')
            elif action == 'apply_crop':
                return self._press_shortcut('crop_apply')
            elif action == 'reset_crop':
                return self._press_shortcut('reset_crop')

            # Rotation commands
            elif action == 'rotate_left':
                return self._press_shortcut('rotate_left')
            elif action == 'rotate_right':
                return self._press_shortcut('rotate_right')
            elif action == 'flip_horizontal':
                return self._flip_horizontal()
            elif action == 'flip_vertical':
                return self._flip_vertical()

            # Copy/Paste commands
            elif action == 'copy_adjustments':
                return self._press_shortcut('copy_adjustments')
            elif action == 'paste_adjustments':
                return self._press_shortcut('paste_adjustments')

            # View commands
            elif action == 'fullscreen':
                return self._press_shortcut('fullscreen')
            elif action == 'exit_fullscreen':
                return self._press_shortcut('fullscreen')  # Toggle
            elif action == 'zoom_to_fit':
                return self._press_shortcut('zoom_to_fit')
            elif action == 'zoom_100':
                return self._press_shortcut('zoom_100')
            elif action == 'zoom_in':
                return self._press_shortcut('zoom_in')
            elif action == 'zoom_out':
                return self._press_shortcut('zoom_out')

            # Comparison commands
            elif action == 'compare':
                return self._press_shortcut('compare')
            elif action == 'before_after':
                return self._press_shortcut('before_after')

            # Focus commands
            elif action == 'show_focus_mask':
                return self._press_shortcut('focus_mask')
            elif action == 'hide_focus_mask':
                return self._press_shortcut('focus_mask')  # Toggle

            # Workflow macro commands
            elif action == 'macro_hero_shot':
                return self._macro_hero_shot()
            elif action == 'macro_selects':
                return self._macro_selects()
            elif action == 'macro_reject':
                return self._macro_reject()
            elif action == 'macro_maybe':
                return self._macro_maybe()

            # Filter/review commands
            elif action == 'filter_flagged':
                return self._filter_flagged()
            elif action == 'filter_5_stars':
                return self._filter_rating(5)
            elif action == 'filter_selects':
                return self._filter_rating_min(4)
            elif action == 'filter_rejects':
                return self._filter_rejected()
            elif action == 'show_last_captures':
                return self._select_last(command.params.get('count'))
            elif action == 'clear_filters':
                return self._clear_filters()
            elif action == 'show_all':
                return self._clear_filters()

            # Exposure/technical check commands
            elif action == 'show_overexposure':
                return self._show_overexposure()
            elif action == 'hide_overexposure':
                return self._hide_overexposure()
            elif action == 'show_histogram':
                return self._show_histogram()
            elif action == 'hide_histogram':
                return self._hide_histogram()

            # Batch operation commands
            elif action == 'batch_apply_to_flagged':
                return self._batch_apply_to_flagged()
            elif action == 'batch_white_balance':
                return self._batch_white_balance()

            else:
                print(f"Unknown action: {action}")
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

    def _adjust_contrast(self, amount: int) -> bool:
        """Adjust contrast by a specific amount"""
        # Placeholder for contrast adjustment
        print(f"Contrast adjustment not fully implemented yet. Amount: {amount}")
        return True

    def _adjust_saturation(self, amount: int) -> bool:
        """Adjust saturation by a specific amount"""
        # Placeholder for saturation adjustment
        print(f"Saturation adjustment not fully implemented yet. Amount: {amount}")
        return True

    def _remove_label(self) -> bool:
        """Remove color label from selected image"""
        # Press Command+0 to remove label
        return self._press_key('command down & 0 & command up')

    def _select_first(self, count: int) -> bool:
        """Select the first N images"""
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Go to first image
                key code 115  -- Home key
                delay 0.1

                -- Select first N images
                repeat {count - 1} times
                    keystroke (down arrow) using shift down
                    delay 0.05
                end repeat
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _select_flagged(self) -> bool:
        """Select all flagged images"""
        # Placeholder - would use filter panel
        print("Select flagged images not fully implemented yet")
        return True

    def _select_rejected(self) -> bool:
        """Select all rejected images"""
        # Placeholder - would use filter panel
        print("Select rejected images not fully implemented yet")
        return True

    def _export_all(self) -> bool:
        """Export all images"""
        # Select all, then export
        if self._press_shortcut('select_all'):
            return self._press_shortcut('export')
        return False

    def _flag_last(self, count: int) -> bool:
        """Flag the last N images"""
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

                -- Flag
                keystroke slash
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _unreject_selected(self) -> bool:
        """Remove reject status from selected image"""
        # Pressing reject again toggles it off
        return self._press_shortcut('reject')

    def _flip_horizontal(self) -> bool:
        """Flip image horizontally"""
        # Use menu bar access
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Navigate to Image menu -> Flip -> Horizontal
                click menu item "Horizontal" of menu "Flip" of menu item "Flip" of menu "Image" of menu bar 1
            end tell
        end tell
        '''

        return self._run_applescript(script)

    def _flip_vertical(self) -> bool:
        """Flip image vertically"""
        # Use menu bar access
        script = f'''
        tell application "{self.app_name}"
            activate
        end tell

        delay 0.1

        tell application "System Events"
            tell process "{self.app_name}"
                -- Navigate to Image menu -> Flip -> Vertical
                click menu item "Vertical" of menu "Flip" of menu item "Flip" of menu "Image" of menu bar 1
            end tell
        end tell
        '''

        return self._run_applescript(script)

    # ============================================================
    # WORKFLOW MACRO IMPLEMENTATIONS
    # ============================================================

    def _macro_hero_shot(self) -> bool:
        """Mark as hero shot: 5 stars + green label + flag"""
        # Rate 5 stars
        if not self._rate_selected(5):
            return False
        # Label green
        if not self._label_selected('green'):
            return False
        # Flag
        return self._press_shortcut('flag')

    def _macro_selects(self) -> bool:
        """Mark as selects: 4 stars + flag"""
        # Rate 4 stars
        if not self._rate_selected(4):
            return False
        # Flag
        return self._press_shortcut('flag')

    def _macro_reject(self) -> bool:
        """Mark as reject: reject status"""
        return self._press_shortcut('reject')

    def _macro_maybe(self) -> bool:
        """Mark as maybe: 3 stars + yellow label"""
        # Rate 3 stars
        if not self._rate_selected(3):
            return False
        # Label yellow
        return self._label_selected('yellow')

    # ============================================================
    # FILTER/REVIEW COMMAND IMPLEMENTATIONS
    # ============================================================

    def _filter_flagged(self) -> bool:
        """Show only flagged images using filter panel"""
        # Placeholder - would use Capture One's filter panel
        print("Filter flagged not fully implemented yet")
        return True

    def _filter_rating(self, rating: int) -> bool:
        """Show only images with specific rating"""
        # Placeholder - would use Capture One's filter panel
        print(f"Filter by rating {rating} not fully implemented yet")
        return True

    def _filter_rating_min(self, min_rating: int) -> bool:
        """Show only images with rating >= min_rating"""
        # Placeholder - would use Capture One's filter panel
        print(f"Filter by minimum rating {min_rating} not fully implemented yet")
        return True

    def _filter_rejected(self) -> bool:
        """Show only rejected images"""
        # Placeholder - would use Capture One's filter panel
        print("Filter rejected not fully implemented yet")
        return True

    def _clear_filters(self) -> bool:
        """Clear all active filters"""
        # Cmd+Shift+A clears filters in some views
        return self._press_key('command down & shift down & a & shift up & command up')

    # ============================================================
    # EXPOSURE/TECHNICAL CHECK IMPLEMENTATIONS
    # ============================================================

    def _show_overexposure(self) -> bool:
        """Show overexposure/clipping warning"""
        # Toggle with 'O' key or Cmd+Shift+O
        return self._press_key('o')

    def _hide_overexposure(self) -> bool:
        """Hide overexposure warning"""
        return self._press_key('o')  # Toggle

    def _show_histogram(self) -> bool:
        """Show histogram"""
        # Placeholder - would open histogram tool
        print("Show histogram not fully implemented yet")
        return True

    def _hide_histogram(self) -> bool:
        """Hide histogram"""
        print("Hide histogram not fully implemented yet")
        return True

    # ============================================================
    # BATCH OPERATION IMPLEMENTATIONS
    # ============================================================

    def _batch_apply_to_flagged(self) -> bool:
        """Apply current adjustments to all flagged images"""
        # Copy current adjustments
        if not self._press_shortcut('copy_adjustments'):
            return False

        # Select all flagged (placeholder - would use filter)
        # Then paste adjustments
        return self._press_shortcut('paste_adjustments')

    def _batch_white_balance(self) -> bool:
        """Sync white balance to selected/flagged images"""
        # Placeholder for white balance sync
        print("Batch white balance not fully implemented yet")
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
