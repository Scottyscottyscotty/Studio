"""
Command Parser for Studio
Parses natural language voice commands into structured actions with semantic flexibility
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
    """Parses voice commands into structured Command objects with flexible semantic understanding"""

    def __init__(self):
        # Semantic synonyms for natural language flexibility
        self.synonyms = {
            'delete': r'(?:delete|remove|trash|discard|get rid of)',
            'image': r'(?:image|images|photo|photos|picture|pictures|shot|shots|pic|pics)',
            'selected': r'(?:current|selected|this|that|these|those)',
            'mark': r'(?:mark|rate|set|give|assign)',
            'label': r'(?:label|tag|mark|color)',
            'increase': r'(?:increase|raise|boost|bump up|turn up|up)',
            'decrease': r'(?:decrease|lower|reduce|bring down|turn down|down)',
            'exposure': r'(?:exposure|brightness)',
            'next': r'(?:next|forward)',
            'previous': r'(?:previous|prev|back|prior)',
            'flag': r'(?:flag|star|favorite|favourite|fav)',
            'unflag': r'(?:unflag|unstar|unfavorite|unfavourite)',
            'reject': r'(?:reject|trash|bad)',
            'export': r'(?:export|save|output|render)',
            'select': r'(?:select|choose|pick|highlight|show)',
            'all': r'(?:all|every|everything)',
            'copy': r'(?:copy|duplicate)',
            'paste': r'(?:paste|apply)',
        }

        # Build comprehensive command patterns
        self.patterns = self._build_patterns()

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

    def _s(self, key: str) -> str:
        """Get synonym pattern for a key"""
        return self.synonyms.get(key, key)

    def _word_to_number(self, word: str) -> int:
        """Convert word numbers to integers"""
        word_map = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        return word_map.get(word.lower(), 0)

    def _build_patterns(self) -> list:
        """Build all command patterns with semantic flexibility"""
        return [
            # ============================================================
            # DELETE COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("delete")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}',
                'action': 'delete_last',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("delete")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'delete_selected',
                'params': lambda m: {}
            },

            # ============================================================
            # RATING COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("mark")}\s+(?:the\s+)?last\s+{self._s("image")}\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_last',
                'params': lambda m: {'count': 1, 'rating': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("mark")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_last',
                'params': lambda m: {'count': int(m.group(1)), 'rating': int(m.group(2))}
            },
            {
                'pattern': rf'{self._s("mark")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}\s+(?:as\s+)?(\d+)\s+star',
                'action': 'rate_selected',
                'params': lambda m: {'rating': int(m.group(1))}
            },
            # Zero star rating (unrate)
            {
                'pattern': rf'(?:unrate|remove rating|clear rating)\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'rate_selected',
                'params': lambda m: {'rating': 0}
            },
            # Word number ratings: "mark this five stars"
            {
                'pattern': rf'{self._s("mark")}\s+{self._s("selected")}\s+(zero|one|two|three|four|five)\s+star',
                'action': 'rate_selected',
                'params': lambda m: {'rating': self._word_to_number(m.group(1))}
            },

            # ============================================================
            # COLOR LABEL COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("label")}\s+(?:the\s+)?last\s+{self._s("image")}\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_last',
                'params': lambda m: {'count': 1, 'color': m.group(1)}
            },
            {
                'pattern': rf'{self._s("label")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_last',
                'params': lambda m: {'count': int(m.group(1)), 'color': m.group(2)}
            },
            {
                'pattern': rf'{self._s("label")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}\s+(?:as\s+)?(red|green|blue|yellow|purple|orange|white)',
                'action': 'label_selected',
                'params': lambda m: {'color': m.group(1)}
            },
            # Remove label
            {
                'pattern': rf'(?:remove|clear)\s+(?:the\s+)?(?:label|color)\s+(?:from\s+)?(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'remove_label',
                'params': lambda m: {}
            },

            # ============================================================
            # SELECTION COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("select")}\s+{self._s("all")}\s+{self._s("image")}\s+with\s+(red|green|blue|yellow|purple|orange|white)\s+(?:label|color)',
                'action': 'select_by_color',
                'params': lambda m: {'color': m.group(1)}
            },
            {
                'pattern': rf'{self._s("select")}\s+{self._s("all")}\s+(\d+)\s+star\s+{self._s("image")}',
                'action': 'select_by_rating',
                'params': lambda m: {'rating': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("select")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}',
                'action': 'select_last',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("select")}\s+(?:the\s+)?first\s+(\d+)\s+{self._s("image")}',
                'action': 'select_first',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("select")}\s+{self._s("all")}',
                'action': 'select_all',
                'params': lambda m: {}
            },
            {
                'pattern': rf'(?:deselect|unselect|clear selection)\s*{self._s("all")}?',
                'action': 'deselect_all',
                'params': lambda m: {}
            },
            # Select flagged/rejected
            {
                'pattern': rf'{self._s("select")}\s+{self._s("all")}\s+(?:flagged|starred)\s+{self._s("image")}',
                'action': 'select_flagged',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("select")}\s+{self._s("all")}\s+rejected\s+{self._s("image")}',
                'action': 'select_rejected',
                'params': lambda m: {}
            },

            # ============================================================
            # EXPORT COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("export")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'export_selected',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("export")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}',
                'action': 'export_last',
                'params': lambda m: {'count': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("export")}\s+{self._s("all")}',
                'action': 'export_all',
                'params': lambda m: {}
            },

            # ============================================================
            # ADJUSTMENT COMMANDS
            # ============================================================
            # Exposure
            {
                'pattern': rf'{self._s("increase")}\s+(?:the\s+)?{self._s("exposure")}\s+(?:by\s+)?(\d+)',
                'action': 'adjust_exposure',
                'params': lambda m: {'amount': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("decrease")}\s+(?:the\s+)?{self._s("exposure")}\s+(?:by\s+)?(\d+)',
                'action': 'adjust_exposure',
                'params': lambda m: {'amount': -int(m.group(1))}
            },
            # Contrast
            {
                'pattern': rf'{self._s("increase")}\s+(?:the\s+)?contrast\s+(?:by\s+)?(\d+)',
                'action': 'adjust_contrast',
                'params': lambda m: {'amount': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("decrease")}\s+(?:the\s+)?contrast\s+(?:by\s+)?(\d+)',
                'action': 'adjust_contrast',
                'params': lambda m: {'amount': -int(m.group(1))}
            },
            # Saturation
            {
                'pattern': rf'{self._s("increase")}\s+(?:the\s+)?saturation\s+(?:by\s+)?(\d+)',
                'action': 'adjust_saturation',
                'params': lambda m: {'amount': int(m.group(1))}
            },
            {
                'pattern': rf'{self._s("decrease")}\s+(?:the\s+)?saturation\s+(?:by\s+)?(\d+)',
                'action': 'adjust_saturation',
                'params': lambda m: {'amount': -int(m.group(1))}
            },
            # Auto-adjust
            {
                'pattern': r'auto\s+(?:adjust|correct|fix)',
                'action': 'auto_adjust',
                'params': lambda m: {}
            },
            # Reset
            {
                'pattern': r'reset\s+(?:all\s+)?(?:adjustments|edits|changes)',
                'action': 'reset_adjustments',
                'params': lambda m: {}
            },

            # ============================================================
            # NAVIGATION COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("next")}\s+{self._s("image")}',
                'action': 'next_image',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("previous")}\s+{self._s("image")}',
                'action': 'previous_image',
                'params': lambda m: {}
            },
            # Simpler navigation without "image/photo"
            {
                'pattern': r'(?:go\s+)?(?:back|previous|prev)',
                'action': 'previous_image',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:go\s+)?(?:forward|next)',
                'action': 'next_image',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:go to|jump to)\s+(?:the\s+)?first\s+(?:image|photo)',
                'action': 'first_image',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:go to|jump to)\s+(?:the\s+)?last\s+(?:image|photo)',
                'action': 'last_image',
                'params': lambda m: {}
            },

            # ============================================================
            # FLAG COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("flag")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'flag_selected',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("unflag")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'unflag_selected',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("flag")}\s+(?:the\s+)?last\s+(\d+)\s+{self._s("image")}',
                'action': 'flag_last',
                'params': lambda m: {'count': int(m.group(1))}
            },

            # ============================================================
            # REJECT COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("reject")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'reject_selected',
                'params': lambda m: {}
            },
            {
                'pattern': rf'(?:unreject|un-reject)\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}',
                'action': 'unreject_selected',
                'params': lambda m: {}
            },

            # ============================================================
            # CROP COMMANDS
            # ============================================================
            {
                'pattern': r'(?:enable|start|begin)\s+(?:crop|cropping)',
                'action': 'enable_crop',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:disable|cancel|stop|exit)\s+(?:crop|cropping)',
                'action': 'disable_crop',
                'params': lambda m: {}
            },
            {
                'pattern': r'apply\s+(?:crop|cropping)',
                'action': 'apply_crop',
                'params': lambda m: {}
            },
            {
                'pattern': r'reset\s+crop',
                'action': 'reset_crop',
                'params': lambda m: {}
            },

            # ============================================================
            # ROTATION COMMANDS
            # ============================================================
            {
                'pattern': r'rotate\s+(?:left|counterclockwise|counter-clockwise)',
                'action': 'rotate_left',
                'params': lambda m: {}
            },
            {
                'pattern': r'rotate\s+(?:right|clockwise)',
                'action': 'rotate_right',
                'params': lambda m: {}
            },
            {
                'pattern': r'flip\s+(?:horizontal|horizontally)',
                'action': 'flip_horizontal',
                'params': lambda m: {}
            },
            {
                'pattern': r'flip\s+(?:vertical|vertically)',
                'action': 'flip_vertical',
                'params': lambda m: {}
            },

            # ============================================================
            # COPY/PASTE STYLE COMMANDS
            # ============================================================
            {
                'pattern': rf'{self._s("copy")}\s+(?:adjustments|edits|settings|style)',
                'action': 'copy_adjustments',
                'params': lambda m: {}
            },
            {
                'pattern': rf'{self._s("paste")}\s+(?:adjustments|edits|settings|style)',
                'action': 'paste_adjustments',
                'params': lambda m: {}
            },

            # ============================================================
            # VIEW COMMANDS
            # ============================================================
            {
                'pattern': r'(?:show|enter)\s+(?:full\s*screen|fullscreen)',
                'action': 'fullscreen',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:exit|leave)\s+(?:full\s*screen|fullscreen)',
                'action': 'exit_fullscreen',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:zoom|fit)\s+to\s+(?:fit|screen)',
                'action': 'zoom_to_fit',
                'params': lambda m: {}
            },
            {
                'pattern': r'zoom\s+(?:to\s+)?(?:100|one hundred)\s*(?:percent|%)?',
                'action': 'zoom_100',
                'params': lambda m: {}
            },
            {
                'pattern': r'zoom\s+in',
                'action': 'zoom_in',
                'params': lambda m: {}
            },
            {
                'pattern': r'zoom\s+out',
                'action': 'zoom_out',
                'params': lambda m: {}
            },

            # ============================================================
            # COMPARISON COMMANDS
            # ============================================================
            {
                'pattern': r'(?:compare|show comparison)',
                'action': 'compare',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:show|view)\s+before\s+(?:and\s+)?after',
                'action': 'before_after',
                'params': lambda m: {}
            },

            # ============================================================
            # FOCUS COMMANDS
            # ============================================================
            {
                'pattern': r'(?:enable|show)\s+focus\s+mask',
                'action': 'show_focus_mask',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:disable|hide)\s+focus\s+mask',
                'action': 'hide_focus_mask',
                'params': lambda m: {}
            },

            # ============================================================
            # WORKFLOW MACRO COMMANDS
            # ============================================================
            # Hero shot - 5 stars + green label + flag
            {
                'pattern': r'(?:mark|tag|set)\s+(?:as\s+)?(?:hero|keeper|best)(?:\s+shot)?',
                'action': 'macro_hero_shot',
                'params': lambda m: {}
            },
            # Selects - 4 stars + flag
            {
                'pattern': r'(?:mark|tag|set)\s+(?:as\s+)?(?:select|selects|good)',
                'action': 'macro_selects',
                'params': lambda m: {}
            },
            # Rejects - reject + 1 star
            {
                'pattern': r'(?:mark|tag|set)\s+(?:as\s+)?(?:reject|bad|trash|dud)(?:s)?',
                'action': 'macro_reject',
                'params': lambda m: {}
            },
            # Maybe - 3 stars + yellow label
            {
                'pattern': r'(?:mark|tag|set)\s+(?:as\s+)?(?:maybe|review|check)',
                'action': 'macro_maybe',
                'params': lambda m: {}
            },

            # ============================================================
            # QUICK REVIEW/FILTER COMMANDS
            # ============================================================
            # Show only flagged
            {
                'pattern': r'(?:show|display|view)\s+(?:only\s+)?(?:flagged|favorites|starred)(?:\s+images)?',
                'action': 'filter_flagged',
                'params': lambda m: {}
            },
            # Show only 5 stars
            {
                'pattern': r'(?:show|display|view)\s+(?:only\s+)?(?:5|five)\s+star(?:s)?(?:\s+images)?',
                'action': 'filter_5_stars',
                'params': lambda m: {}
            },
            # Show only 4+ stars (selects)
            {
                'pattern': r'(?:show|display|view)\s+(?:only\s+)?(?:selects|4 plus|four plus)',
                'action': 'filter_selects',
                'params': lambda m: {}
            },
            # Show only rejects
            {
                'pattern': r'(?:show|display|view)\s+(?:only\s+)?reject(?:s|ed)?(?:\s+images)?',
                'action': 'filter_rejects',
                'params': lambda m: {}
            },
            # Show last N captures
            {
                'pattern': r'(?:show|display|view)\s+(?:the\s+)?last\s+(\d+)\s+capture(?:s)?',
                'action': 'show_last_captures',
                'params': lambda m: {'count': int(m.group(1))}
            },
            # Clear all filters
            {
                'pattern': r'(?:clear|remove|reset)\s+(?:all\s+)?filter(?:s)?',
                'action': 'clear_filters',
                'params': lambda m: {}
            },
            # Show all images
            {
                'pattern': r'(?:show|display|view)\s+(?:all|everything)',
                'action': 'show_all',
                'params': lambda m: {}
            },

            # ============================================================
            # EXPOSURE/TECHNICAL CHECK COMMANDS
            # ============================================================
            {
                'pattern': r'(?:show|enable|display)\s+(?:overexposure|clipping)\s+(?:warning|indicator)',
                'action': 'show_overexposure',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:hide|disable)\s+(?:overexposure|clipping)\s+(?:warning|indicator)',
                'action': 'hide_overexposure',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:show|enable|display)\s+histogram',
                'action': 'show_histogram',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:hide|disable)\s+histogram',
                'action': 'hide_histogram',
                'params': lambda m: {}
            },

            # ============================================================
            # BATCH OPERATIONS
            # ============================================================
            {
                'pattern': r'(?:apply|sync)\s+(?:these\s+)?(?:settings|adjustments|edits)\s+to\s+(?:all\s+)?(?:flagged|selected)',
                'action': 'batch_apply_to_flagged',
                'params': lambda m: {}
            },
            {
                'pattern': r'(?:apply|sync)\s+white\s+balance\s+to\s+(?:all\s+)?(?:flagged|selected)',
                'action': 'batch_white_balance',
                'params': lambda m: {}
            },
        ]

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
        # Original tests
        "Studio, delete the last 4 images",
        "Studio, mark the last image as 5 stars",
        "Studio, select all images with red labels",

        # Semantic variations
        "Studio, trash that picture",
        "Studio, remove these photos",
        "Studio, rate this shot as 4 stars",
        "Studio, give that image 3 stars",
        "Studio, tag this pic as blue",
        "Studio, boost the exposure by 10",
        "Studio, turn down the brightness by 5",
        "Studio, jump to the next photo",
        "Studio, go back",
        "Studio, favorite this image",
        "Studio, copy adjustments",
        "Studio, show fullscreen",
        "Studio, auto adjust",

        # Should not match
        "Not a studio command"
    ]

    print("Testing Command Parser with Semantic Variations:")
    print("=" * 70)
    for cmd_text in test_commands:
        result = parser.parse(cmd_text)
        status = "✓" if result else "✗"
        print(f"{status} Input:  {cmd_text}")
        print(f"  Output: {result}")
        print()
