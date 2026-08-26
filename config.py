"""
Studio Configuration
All settings in one place
"""

import pyaudio


class Config:
    """Application configuration - change settings here"""

    # Version
    VERSION = "3.0"

    # Audio Recording
    AUDIO_CHUNK_SIZE = 1024
    AUDIO_FORMAT = pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_SAMPLE_RATE = 16000
    RECORDING_TIMEOUT = 5  # seconds

    # OpenAI API
    WHISPER_MODEL = "whisper-1"
    WHISPER_LANGUAGE = "en"
    COMMAND_PARSER_MODEL = "gpt-4o-mini"  # Fast & cheap for command parsing
    TTS_MODEL = "tts-1"
    TTS_VOICE = "nova"
    TTS_SPEED = 1.2
    API_TIMEOUT = 30.0

    # App Behavior
    MAX_COMMAND_HISTORY = 10
    TTS_CLEANUP_DELAY = 5.0
    CONTINUOUS_MODE_RESTART_DELAY = 1.0

    # Capture One
    CAPTURE_ONE_APP_NAME = "Capture One"  # Override if different version
