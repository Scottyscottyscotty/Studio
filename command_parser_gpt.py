"""
GPT-4 Command Parser
Replaces 648 lines of regex with ~50 lines of natural language understanding
"""

import json
from typing import Optional
from openai import OpenAI


class GPT4CommandParser:
    """Parse voice commands using GPT-4 function calling"""

    def __init__(self, openai_client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = openai_client
        self.model = model

        # Define available commands as a function schema
        self.function_schema = {
            "name": "execute_capture_one_command",
            "description": "Execute a voice command in Capture One Pro photo editing software",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "rate", "label", "delete", "select", "export",
                            "flag", "reject", "rotate", "flip", "crop",
                            "navigate", "adjust", "zoom", "compare",
                            "auto_adjust", "reset", "copy_adjustments", "paste_adjustments"
                        ],
                        "description": "The action to perform"
                    },
                    "target": {
                        "type": "string",
                        "enum": ["selected", "last", "first", "all", "next", "previous"],
                        "description": "Which image(s) to act on. 'selected' = current/this image"
                    },
                    "value": {
                        "type": "integer",
                        "description": "Rating (1-5), count of images, adjustment amount, or None",
                        "minimum": -100,
                        "maximum": 100
                    },
                    "color": {
                        "type": "string",
                        "enum": ["red", "green", "blue", "yellow", "purple", "orange", "white"],
                        "description": "Color for labeling"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["left", "right", "horizontal", "vertical"],
                        "description": "Direction for rotate/flip"
                    }
                },
                "required": ["action", "target"]
            }
        }

    def parse(self, text: str) -> Optional[dict]:
        """
        Parse natural language command using GPT-4

        Args:
            text: Voice command (e.g. "Studio mark this image 3 stars")

        Returns:
            Command dict or None if not recognized
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a voice command parser for Capture One Pro. "
                                   "Parse user commands into structured actions. "
                                   "'this/that' = selected (current image), "
                                   "'these/those' = all (multiple images)."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                functions=[self.function_schema],
                function_call={"name": "execute_capture_one_command"},
                temperature=0  # Deterministic parsing
            )

            # Extract function call arguments
            function_call = response.choices[0].message.function_call
            if function_call:
                command = json.loads(function_call.arguments)
                print(f"[DEBUG] GPT-4 parsed: {command}")
                return command

            return None

        except Exception as e:
            print(f"[ERROR] GPT-4 parsing failed: {e}")
            return None


# Simple command object for compatibility
class Command:
    """Simplified command object"""
    def __init__(self, **kwargs):
        self.action = kwargs.get('action')
        self.target = kwargs.get('target', 'selected')
        self.value = kwargs.get('value')
        self.color = kwargs.get('color')
        self.direction = kwargs.get('direction')

    def __repr__(self):
        return f"Command(action={self.action}, target={self.target}, value={self.value})"
