"""
Command Parser for Studio
Parses natural language voice commands into structured actions
"""

import re
from typing import Optional, Dict, Any


class Command:
    """Represents a parsed command"""

    def __init__(self, action: str, **kwargs):
        self.action = action
        self.params = kwargs

    def __repr__(self):
        return f"Command(action='{self.action}', params={self.params})"


class CommandParser:
    """Parses voice commands into structured Command objects"""

    def __init__(self):
        # Define command patterns
        self.patterns = [
            # Delete commands
            {
                'pattern': r'delete\s+(?:the\s+)?last\s+(\d+)\s+(?:image|images|photo|photos)',
                'action': 'delete_last',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': r'delete\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)',
                'action': 'delete_selected',
                'params': lambda m: {}
            },

            # Rating commands
            {
                'pattern': r'(?:mark|rate|set)\s+(?:the\s+)?last\s+(?:image|photo)\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_last',
                'params': lambda m: {'count': 1, 'rating': int(m.group(1))}
            },
            {
                'pattern': r'(?:mark|rate|set)\s+(?:the\s+)?last\s+(\d+)\s+(?:images|photos)\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_last',
                'params': lambda m: {'count': int(m.group(1)), 'rating': int(m.group(2))}
            },
            {
                'pattern': r'(?:mark|rate|set)\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_selected',
                'params': lambda m: {'rating': int(m.group(1))}
            },

            # Color label commands
            {
                'pattern': r'(?:mark|label|tag)\s+(?:the\s+)?last\s+(?:image|photo)\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_last',
                'params': lambda m: {'count': 1, 'color': m.group(1)}
            },
            {
                'pattern': r'(?:mark|label|tag)\s+(?:the\s+)?last\s+(\d+)\s+(?:images|photos)\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_last',
                'params': lambda m: {'count': int(m.group(1)), 'color': m.group(2)}
            },
            {
                'pattern': r'(?:mark|label|tag)\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_selected',
                'params': lambda m: {'color': m.group(1)}
            },

            # Selection commands
            {
                'pattern': r'select\s+(?:all\s+)?(?:images|photos)\s+with\s+(red|green|blue|yellow|purple|orange|white)\s+label',
                'action': 'select_by_color',
                'params': lambda m: {'color': m.group(1)}
            },
            {
                'pattern': r'select\s+(?:all\s+)?(\d+)\s+star\s+(?:images|photos)',
                'action': 'select_by_rating',
                'params': lambda m: {'rating': int(m.group(1))}
            },
            {
                'pattern': r'select\s+(?:the\s+)?last\s+(\d+)\s+(?:images|photos)',
                'action': 'select_last',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': r'select\s+(?:all|everything)',
                'action': 'select_all',
                'params': lambda m: {}
            },
            {
                'pattern': r'deselect\s+(?:all|everything)',
                'action': 'deselect_all',
                'params': lambda m: {}
            },

            # Export commands
            {
                'pattern': r'export\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|images|photo|photos)',
                'action': 'export_selected',
                'params': lambda m: {}
            },
            {
                'pattern': r'export\s+(?:the\s+)?last\s+(\d+)\s+(?:images|photos)',
                'action': 'export_last',
                'params': lambda m: {'count': int(m.group(1))}
            },

            # Adjustment commands
            {
                'pattern': r'(?:increase|raise|boost)\s+(?:the\s+)?exposure\s+(?:by\s+)?(\d+)',
                'action': 'adjust_exposure',
                'params': lambda m: {'amount': int(m.group(1))}
            },
            {
                'pattern': r'(?:decrease|lower|reduce)\s+(?:the\s+)?exposure\s+(?:by\s+)?(\d+)',
                'action': 'adjust_exposure',
                'params': lambda m: {'amount': -int(m.group(1))}
            },
            {
                'pattern': r'reset\s+(?:all\s+)?adjustments',
                'action': 'reset_adjustments',
                'params': lambda m: {}
            },

            # Next/Previous commands
            {
                'pattern': r'(?:next|forward)\s+(?:image|photo)',
                'action': 'next_image',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:previous|back|last)\s+(?:image|photo)',
                'action': 'previous_image',
                'params': lambda m: {}
            },

            # Flag commands
            {
                'pattern': r'flag\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)',
                'action': 'flag_selected',
                'params': lambda m: {}
            },
            {
                'pattern': r'unflag\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)',
                'action': 'unflag_selected',
                'params': lambda m: {}
            },

            # Reject commands
            {
                'pattern': r'reject\s+(?:the\s+)?(?:current|selected|this)\s+(?:image|photo)',
                'action': 'reject_selected',
                'params': lambda m: {}
            },

            # Crop commands
            {
                'pattern': r'(?:enable|start)\s+crop',
                'action': 'enable_crop',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:disable|cancel|stop)\s+crop',
                'action': 'disable_crop',
                'params': lambda m: {}
            },
            {
                'pattern': r'apply\s+crop',
                'action': 'apply_crop',
                'params': lambda m: {}
            },
        ]

        # Color label mappings
        self.color_labels = {
            'red': 'red',
            'green': 'green',
            'blue': 'blue',
            'yellow': 'yellow',
            'purple': 'purple',
            'orange': 'orange',
            'white': 'white'
        }

    def parse(self, text: str) -> Optional[Command]:
        """
        Parse a voice command text into a Command object

        Args:
            text: The transcribed voice command

        Returns:
            A Command object if the command is recognized, None otherwise
        """
        # Normalize the text
        text = text.lower().strip()

        # Check if the command starts with the wake word "studio"
        if not self._has_wake_word(text):
            return None

        # Remove the wake word and any following punctuation
        command_text = self._remove_wake_word(text)

        # Try to match against all patterns
        for pattern_def in self.patterns:
            match = re.search(pattern_def['pattern'], command_text, re.IGNORECASE)
            if match:
                action = pattern_def['action']
                params = pattern_def['params'](match)
                return Command(action, **params)

        # No pattern matched
        return None

    def _has_wake_word(self, text: str) -> bool:
        """Check if the text contains the wake word 'studio'"""
        return bool(re.search(r'\bstudio\b', text, re.IGNORECASE))

    def _remove_wake_word(self, text: str) -> str:
        """Remove the wake word and any following punctuation from the text"""
        # Remove "studio" and any following comma, period, or whitespace
        text = re.sub(r'\bstudio\b[\s,.:;]*', '', text, flags=re.IGNORECASE)
        return text.strip()


# Test function for development
if __name__ == "__main__":
    parser = CommandParser()

    test_commands = [
        "Studio, delete the last 4 images",
        "Studio, mark the last image as 5 stars",
        "Studio, select all images with red labels",
        "Studio, export the current image",
        "Studio, increase the exposure by 10",
        "Studio, next image",
        "Hey Studio, flag this photo",
        "Studio rate the last 3 images as 4 stars",
        "Not a studio command"
    ]

    print("Testing Command Parser:")
    print("-" * 60)
    for cmd_text in test_commands:
        result = parser.parse(cmd_text)
        print(f"Input:  {cmd_text}")
        print(f"Output: {result}")
        print()
