#!/usr/bin/env python3
"""
Studio v3.0 - Voice Assistant for Capture One
Simplified, clean, scalable architecture
"""

import rumps
import os
import sys
import threading
import wave
import pyaudio
import subprocess
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

from config import Config
from command_parser_gpt import GPT4CommandParser
from capture_one_simple import CaptureOneController

# Load environment variables
load_dotenv()


class StudioApp(rumps.App):
    """Main Studio application - clean and simple"""

    def __init__(self):
        super().__init__("Studio", icon=None, quit_button=None)

        # Initialize OpenAI
        self.openai_client = self._init_openai()

        # Initialize components
        self.parser = GPT4CommandParser(self.openai_client, Config.COMMAND_PARSER_MODEL)
        self.capture_one = CaptureOneController(Config.CAPTURE_ONE_APP_NAME)

        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.audio_frames = []

        # State
        self.continuous_mode = False
        self.voice_feedback = True

        # Create recordings directory
        self.recordings_dir = Path.home() / ".studio" / "recordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        # Build menu
        self.menu = [
            rumps.MenuItem("Start Listening ⏺", callback=self.toggle_recording),
            rumps.MenuItem("Continuous Mode: Off", callback=self.toggle_continuous),
            rumps.separator,
            rumps.MenuItem("Voice Feedback: On", callback=self.toggle_feedback),
            rumps.separator,
            rumps.MenuItem("Status: Ready", callback=None),
            rumps.separator,
            rumps.MenuItem("About", callback=self.show_about),
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

    def _init_openai(self) -> OpenAI:
        """Initialize and test OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            rumps.alert("API Key Required", "Set OPENAI_API_KEY in .env file")
            sys.exit(1)

        client = OpenAI(api_key=api_key, timeout=Config.API_TIMEOUT)

        # Test connection
        try:
            client.models.list()
            print("[INFO] OpenAI connected successfully")
        except AuthenticationError:
            rumps.alert("Invalid API Key", "Check your .env file")
            sys.exit(1)
        except APIConnectionError:
            rumps.alert("Connection Error", "Check your internet connection")
            sys.exit(1)

        return client

    # ============================================================
    # MENU ACTIONS
    # ============================================================

    def toggle_recording(self, sender):
        """Toggle listening on/off"""
        if not self.is_recording:
            self.start_listening(sender)
        else:
            self.stop_listening(sender)

    def start_listening(self, sender):
        """Start recording audio"""
        self.is_recording = True
        sender.title = "Stop Listening ⏹"
        self._update_status("Listening...")
        self.title = "Studio 🎤"

        # Record in background
        threading.Thread(target=self._record_audio, daemon=True).start()

        # Auto-stop after timeout
        threading.Timer(Config.RECORDING_TIMEOUT, lambda: self.stop_listening(sender)).start()

    def stop_listening(self, sender):
        """Stop recording and process"""
        if not self.is_recording:
            return

        self.is_recording = False
        sender.title = "Start Listening ⏺"
        self._update_status("Processing...")

        # Process in background
        threading.Thread(target=self._process_audio, daemon=True).start()

    def toggle_continuous(self, sender):
        """Toggle continuous listening mode"""
        self.continuous_mode = not self.continuous_mode
        sender.title = f"Continuous Mode: {'On' if self.continuous_mode else 'Off'}"

        if self.continuous_mode:
            self._speak("Continuous mode enabled")
            self._start_continuous_listening()
        else:
            self._speak("Continuous mode disabled")

    def toggle_feedback(self, sender):
        """Toggle voice feedback"""
        self.voice_feedback = not self.voice_feedback
        sender.title = f"Voice Feedback: {'On' if self.voice_feedback else 'Off'}"

    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            "Studio v3.0",
            "Voice Assistant for Capture One\n\n"
            "Clean, simple, scalable architecture\n"
            "Powered by GPT-4 + Whisper + TTS"
        )

    def quit_app(self, _):
        """Clean shutdown"""
        self.audio.terminate()
        rumps.quit_application()

    # ============================================================
    # AUDIO PROCESSING
    # ============================================================

    def _record_audio(self):
        """Record audio from microphone"""
        self.audio_frames = []

        try:
            stream = self.audio.open(
                format=Config.AUDIO_FORMAT,
                channels=Config.AUDIO_CHANNELS,
                rate=Config.AUDIO_SAMPLE_RATE,
                input=True,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE
            )

            while self.is_recording:
                data = stream.read(Config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                self.audio_frames.append(data)

            stream.stop_stream()
            stream.close()

        except Exception as e:
            print(f"[ERROR] Recording failed: {e}")
            self.is_recording = False

    def _process_audio(self):
        """Process recorded audio → command → execution"""
        try:
            # Save audio to file
            if not self.audio_frames:
                print("[DEBUG] No audio recorded")
                self._restart_if_continuous()
                return

            audio_file = self.recordings_dir / "temp.wav"
            with wave.open(str(audio_file), 'wb') as wf:
                wf.setnchannels(Config.AUDIO_CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(Config.AUDIO_FORMAT))
                wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                wf.writeframes(b''.join(self.audio_frames))

            # Transcribe with Whisper
            print("[DEBUG] Transcribing...")
            transcription = self._transcribe(audio_file)

            if not transcription:
                print("[DEBUG] No speech detected")
                self._restart_if_continuous()
                return

            print(f"[DEBUG] Transcribed: '{transcription}'")

            # Parse with GPT-4
            command = self.parser.parse(transcription)

            if not command:
                print("[DEBUG] Command not recognized")
                self._speak("Command not recognized")
                self._restart_if_continuous()
                return

            # Execute in Capture One
            success = self.capture_one.execute(command)

            if success:
                self._speak(self._get_feedback(command))
                self._update_status("Success")
            else:
                self._speak("Command failed")
                self._update_status("Failed")

            self._restart_if_continuous()

        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")
            self._restart_if_continuous()

    def _transcribe(self, audio_file: Path) -> str:
        """Transcribe audio file with Whisper"""
        try:
            with open(audio_file, 'rb') as f:
                transcript = self.openai_client.audio.transcriptions.create(
                    model=Config.WHISPER_MODEL,
                    file=("audio.wav", f, "audio/wav"),
                    language=Config.WHISPER_LANGUAGE
                )
            return transcript.text.strip()

        except RateLimitError:
            print("[ERROR] Rate limited")
            return ""
        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}")
            return ""

    def _speak(self, text: str):
        """Speak text with OpenAI TTS"""
        if not self.voice_feedback:
            return

        try:
            response = self.openai_client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                speed=Config.TTS_SPEED
            )

            # Handle both streaming and direct responses
            if hasattr(response, 'read') and callable(response.read):
                content = response.read()
            elif hasattr(response, 'content'):
                content = response.content
            else:
                return

            # Play audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                f.write(content)
                temp_path = f.name

            subprocess.Popen(['afplay', temp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Clean up later
            threading.Timer(Config.TTS_CLEANUP_DELAY, lambda: Path(temp_path).unlink(missing_ok=True)).start()

        except Exception as e:
            print(f"[ERROR] TTS failed: {e}")

    # ============================================================
    # HELPERS
    # ============================================================

    def _get_feedback(self, command: dict) -> str:
        """Generate friendly feedback"""
        action = command.get('action')
        value = command.get('value')

        feedback = {
            'rate': f"Rated {value} stars",
            'label': f"Labeled {command.get('color')}",
            'delete': "Deleted",
            'flag': "Flagged",
            'reject': "Rejected",
            'export': "Exporting",
            'navigate': "Navigating",
        }

        return feedback.get(action, "Done")

    def _update_status(self, message: str):
        """Update status in menu"""
        for item in self.menu.values():
            if hasattr(item, 'title') and item.title and item.title.startswith("Status:"):
                item.title = f"Status: {message}"
                break

        # Update app title
        if "Listening" in message:
            self.title = "Studio 🎤"
        elif message in ["Ready", "Success"]:
            self.title = "Studio"
        else:
            self.title = "Studio ⏳"

    def _start_continuous_listening(self):
        """Start continuous listening mode"""
        if not self.is_recording:
            threading.Thread(target=self._continuous_listen, daemon=True).start()

    def _continuous_listen(self):
        """Continuous listening loop"""
        self.is_recording = True
        self._update_status("Listening...")

        threading.Thread(target=self._record_audio, daemon=True).start()
        threading.Timer(Config.RECORDING_TIMEOUT, self._process_and_restart).start()

    def _process_and_restart(self):
        """Process and restart continuous listening"""
        if self.is_recording:
            self.is_recording = False
            self._process_audio()

    def _restart_if_continuous(self):
        """Restart listening if in continuous mode"""
        if self.continuous_mode:
            threading.Timer(Config.CONTINUOUS_MODE_RESTART_DELAY, self._continuous_listen).start()
        else:
            self._update_status("Ready")
            self.title = "Studio"


def main():
    """Entry point"""
    StudioApp().run()


if __name__ == "__main__":
    main()
