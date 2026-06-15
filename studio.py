#!/usr/bin/env python3
"""
Studio - Voice Assistant for Capture One
A macOS menu bar application for voice-controlled photo editing with continuous listening
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
from openai import OpenAI
from pynput import keyboard
from collections import deque

from command_parser import CommandParser
from capture_one_controller import CaptureOneController

# Load environment variables
load_dotenv()


# Configuration Constants
class Config:
    """Application configuration"""
    VERSION = "2.1"

    # Audio Recording
    AUDIO_CHUNK_SIZE = 1024
    AUDIO_FORMAT = pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_SAMPLE_RATE = 16000

    # Recording Timeouts (seconds)
    MENU_RECORDING_TIMEOUT = 5
    PROGRAMMATIC_RECORDING_TIMEOUT = 5

    # OpenAI API
    WHISPER_MODEL = "whisper-1"
    WHISPER_LANGUAGE = "en"
    API_TIMEOUT = 30.0

    # Text-to-Speech
    TTS_MODEL = "tts-1"
    TTS_VOICE = "nova"  # Options: alloy, echo, fable, onyx, nova, shimmer
    TTS_SPEED = 1.2
    TTS_CLEANUP_DELAY = 5.0

    # Command History
    MAX_COMMAND_HISTORY = 10


class StudioApp(rumps.App):
    def __init__(self):
        super(StudioApp, self).__init__(
            "Studio",
            icon=None,  # Will show "Studio" text in menu bar
            quit_button=None
        )

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            rumps.alert(
                "OpenAI API Key Required",
                "Please set your OPENAI_API_KEY in the .env file"
            )
            sys.exit(1)

        self.openai_client = OpenAI(api_key=api_key, timeout=Config.API_TIMEOUT)

        # Test API key validity at startup
        print(f"[DEBUG] API key loaded: {api_key[:20]}...{api_key[-4:]}")
        print("[DEBUG] Testing OpenAI API connection...")
        try:
            # Quick test with models endpoint
            self.openai_client.models.list()
            print("[DEBUG] OpenAI API connection successful!")
        except Exception as e:
            print(f"[DEBUG] OpenAI API test failed: {e}")
            rumps.alert(
                "OpenAI API Error",
                f"Failed to connect to OpenAI API: {str(e)}"
            )

        # Initialize components
        self.command_parser = CommandParser()
        self.capture_one = CaptureOneController()

        # Audio recording settings
        self.is_recording = False
        self.audio_frames = []
        self.audio = pyaudio.PyAudio()

        # Continuous listening mode
        self.continuous_mode = False
        self.voice_feedback_enabled = True

        # Command history for undo
        self.command_history = deque(maxlen=Config.MAX_COMMAND_HISTORY)
        self.last_command = None

        # Create recordings directory
        self.recordings_dir = Path.home() / ".studio" / "recordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        # Menu items
        self.menu = [
            rumps.MenuItem("Start Listening ⏺", callback=self.toggle_recording),
            rumps.MenuItem("Continuous Mode: Off", callback=self.toggle_continuous_mode),
            rumps.separator,
            rumps.MenuItem("Voice Feedback: On", callback=self.toggle_voice_feedback),
            rumps.separator,
            rumps.MenuItem("Status: Ready", callback=None),
            rumps.separator,
            rumps.MenuItem("Undo Last Command", callback=self.undo_last_command),
            rumps.separator,
            rumps.MenuItem("Settings", callback=self.show_settings),
            rumps.MenuItem("About Studio", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Set up global hotkey (Option+Space)
        # Temporarily disabled due to pynput compatibility issue with Python 3.13
        # self.setup_global_hotkey()

    def setup_global_hotkey(self):
        """Setup global keyboard shortcut for activating listening"""
        def on_activate():
            if not self.is_recording:
                # Trigger listening mode
                self.start_recording_programmatic()

        # Create hotkey combination (Option+Space)
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>+<space>'),
            on_activate
        )

        def for_canonical(f):
            return lambda k: f(self.keyboard_listener.canonical(k))

        self.keyboard_listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )

        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def toggle_continuous_mode(self, sender):
        """Toggle continuous listening mode"""
        self.continuous_mode = not self.continuous_mode

        if self.continuous_mode:
            sender.title = "Continuous Mode: On ✓"
            self._update_status("Continuous mode active")
            self._speak("Continuous listening enabled")
            # Start continuous listening
            if not self.is_recording:
                self.start_recording_programmatic()
        else:
            sender.title = "Continuous Mode: Off"
            self._update_status("Ready")
            self._speak("Continuous listening disabled")

    def toggle_voice_feedback(self, sender):
        """Toggle voice feedback on/off"""
        self.voice_feedback_enabled = not self.voice_feedback_enabled

        if self.voice_feedback_enabled:
            sender.title = "Voice Feedback: On ✓"
            self._speak("Voice feedback enabled")
        else:
            sender.title = "Voice Feedback: Off"

    def toggle_recording(self, sender):
        """Toggle audio recording on/off"""
        if not self.is_recording:
            self.start_recording(sender)
        else:
            self.stop_recording(sender)

    def start_recording_programmatic(self):
        """Start recording without menu item (for hotkey)"""
        if self.is_recording:
            return

        self.is_recording = True
        self._update_status("Listening...")
        self.title = "Studio 🎤"

        # Start recording in a separate thread
        threading.Thread(target=self._record_audio, daemon=True).start()

        # Auto-stop after configured timeout for programmatic recording
        threading.Timer(Config.PROGRAMMATIC_RECORDING_TIMEOUT, self._stop_recording_programmatic).start()

    def start_recording(self, sender):
        """Start recording audio"""
        print("[DEBUG] Start listening clicked")
        self.is_recording = True
        self.menu_recording_sender = sender  # Store sender for auto-stop
        sender.title = "Stop Listening ⏹"
        self._update_status("Listening...")
        self.title = "Studio 🎤"

        # Start recording in a separate thread
        threading.Thread(target=self._record_audio, daemon=True).start()

        # Auto-stop after configured timeout for menu-based recording
        threading.Timer(Config.MENU_RECORDING_TIMEOUT, self._auto_stop_menu_recording).start()

    def stop_recording(self, sender):
        """Stop recording and process the audio"""
        print("[DEBUG] Stop listening clicked")
        self.is_recording = False
        sender.title = "Start Listening ⏺"
        self._update_status("Processing...")
        self.title = "Studio ⏳"

        # Process the recording in a separate thread
        threading.Thread(target=self._process_recording, daemon=True).start()

    def _auto_stop_menu_recording(self):
        """Auto-stop menu-based recording after timeout"""
        if not self.is_recording:
            return

        print("[DEBUG] Auto-stopping menu recording after 5 seconds")
        self.is_recording = False

        # Update menu item if we have the sender
        if hasattr(self, 'menu_recording_sender') and self.menu_recording_sender:
            self.menu_recording_sender.title = "Start Listening ⏺"

        self._update_status("Processing...")
        self.title = "Studio ⏳"

        # Process the recording in a separate thread
        threading.Thread(target=self._process_recording, daemon=True).start()

    def _stop_recording_programmatic(self):
        """Auto-stop recording and process (for hotkey/continuous mode)"""
        if not self.is_recording:
            return

        self.is_recording = False
        self._update_status("Processing...")
        self.title = "Studio ⏳"

        # Process the recording in a separate thread
        threading.Thread(target=self._process_recording, daemon=True).start()

    def _record_audio(self):
        """Record audio from the microphone"""
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
                data = stream.read(CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)

            stream.stop_stream()
            stream.close()

        except Exception as e:
            rumps.notification(
                "Studio Error",
                "Microphone Error",
                str(e)
            )
            self.is_recording = False

    def _process_recording(self):
        """Process the recorded audio through Whisper API"""
        try:
            print(f"\n[DEBUG] Processing {len(self.audio_frames)} audio frames...")

            # Check if we have audio data
            if not self.audio_frames or len(self.audio_frames) == 0:
                print("[DEBUG] No audio frames captured")
                self._update_status("No audio recorded")
                return

            # Save the recording to a file
            audio_file_path = self.recordings_dir / "temp_recording.wav"

            wf = wave.open(str(audio_file_path), 'wb')
            wf.setnchannels(Config.AUDIO_CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(Config.AUDIO_FORMAT))
            wf.setframerate(Config.AUDIO_SAMPLE_RATE)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()

            # Check file size
            file_size = audio_file_path.stat().st_size
            print(f"[DEBUG] Audio saved to: {audio_file_path} (size: {file_size} bytes)")

            # Send to OpenAI Whisper API
            print(f"[DEBUG] Sending to Whisper API... (timeout: {Config.API_TIMEOUT}s)")
            start_time = time.time()

            try:
                with open(audio_file_path, 'rb') as audio_file:
                    print(f"[DEBUG] File opened, calling API...")
                    # Pass file as tuple: (filename, file_object)
                    transcript = self.openai_client.audio.transcriptions.create(
                        model=Config.WHISPER_MODEL,
                        file=("recording.wav", audio_file, "audio/wav"),
                        language=Config.WHISPER_LANGUAGE
                    )
                    elapsed = time.time() - start_time
                    print(f"[DEBUG] API call completed in {elapsed:.2f}s")

                print(f"[DEBUG] Response type: {type(transcript)}")
                print(f"[DEBUG] Response: {transcript}")

                transcribed_text = transcript.text.strip()
                print(f"[DEBUG] Transcribed: '{transcribed_text}'")
            except Exception as api_error:
                elapsed = time.time() - start_time
                print(f"[DEBUG] API call failed after {elapsed:.2f}s: {type(api_error).__name__}: {str(api_error)}")
                raise

            # Parse and execute the command
            if transcribed_text:
                self._execute_command(transcribed_text)
            else:
                print("[DEBUG] No speech detected")
                self._update_status("No speech detected")
                if self.continuous_mode:
                    # Restart listening in continuous mode
                    threading.Timer(0.5, self.start_recording_programmatic).start()

        except Exception as e:
            print(f"[DEBUG] Error processing recording: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            rumps.notification(
                "Studio Error",
                "Processing Error",
                str(e)
            )
            self._update_status("Error occurred")
            if self.continuous_mode:
                # Restart listening even after error
                threading.Timer(1.0, self.start_recording_programmatic).start()

    def _execute_command(self, transcribed_text):
        """Parse and execute the voice command"""
        try:
            print(f"[DEBUG] Parsing command: '{transcribed_text}'")

            # Parse the command
            command = self.command_parser.parse(transcribed_text)

            if command:
                print(f"[DEBUG] Command parsed: action='{command.action}', params={command.params}")

                # Save to history
                self.last_command = (transcribed_text, command)
                self.command_history.append(self.last_command)

                # Execute the command
                print(f"[DEBUG] Executing command in Capture One...")
                success = self.capture_one.execute(command)
                print(f"[DEBUG] Execution result: {success}")

                if success:
                    # Voice feedback
                    feedback_msg = self._get_command_feedback(command)
                    print(f"[DEBUG] Feedback: {feedback_msg}")
                    self._speak(feedback_msg)

                    rumps.notification(
                        "Studio",
                        "Command Executed",
                        feedback_msg
                    )
                    self._update_status("Command executed")
                else:
                    print("[DEBUG] Command execution failed")
                    self._speak("Command failed")
                    rumps.notification(
                        "Studio",
                        "Execution Failed",
                        "Could not execute command in Capture One"
                    )
                    self._update_status("Execution failed")
            else:
                print(f"[DEBUG] Command not recognized: '{transcribed_text}'")
                self._speak("Command not recognized")
                rumps.notification(
                    "Studio",
                    "Command Not Recognized",
                    f'"{transcribed_text}"'
                )
                self._update_status("Command not recognized")

            # Restart continuous listening if enabled
            if self.continuous_mode:
                threading.Timer(0.5, self.start_recording_programmatic).start()

        except Exception as e:
            self._speak("Error occurred")
            rumps.notification(
                "Studio Error",
                "Command Error",
                str(e)
            )
            self._update_status("Error occurred")

            if self.continuous_mode:
                threading.Timer(1.0, self.start_recording_programmatic).start()

    def _get_command_feedback(self, command):
        """Generate human-friendly feedback for command execution"""
        action = command.action
        params = command.params

        # Friendly feedback messages
        feedback_map = {
            'delete_last': f"Deleted {params.get('count', 1)} images",
            'delete_selected': "Deleted selected images",
            'rate_last': f"Rated {params.get('count', 1)} images as {params.get('rating')} stars",
            'rate_selected': f"Rated as {params.get('rating')} stars",
            'label_last': f"Labeled {params.get('count', 1)} images as {params.get('color')}",
            'label_selected': f"Labeled as {params.get('color')}",
            'remove_label': "Removed label",
            'select_last': f"Selected last {params.get('count')} images",
            'select_first': f"Selected first {params.get('count')} images",
            'select_all': "Selected all images",
            'deselect_all': "Cleared selection",
            'export_selected': "Exporting selected images",
            'export_last': f"Exporting last {params.get('count')} images",
            'export_all': "Exporting all images",
            'flag_selected': "Flagged image",
            'unflag_selected': "Unflagged image",
            'flag_last': f"Flagged last {params.get('count')} images",
            'reject_selected': "Rejected image",
            'unreject_selected': "Unrejected image",
            'next_image': "Next image",
            'previous_image': "Previous image",
            'first_image': "First image",
            'last_image': "Last image",
            'rotate_left': "Rotated left",
            'rotate_right': "Rotated right",
            'flip_horizontal': "Flipped horizontal",
            'flip_vertical': "Flipped vertical",
            'auto_adjust': "Auto adjusted",
            'reset_adjustments': "Reset all adjustments",
            'copy_adjustments': "Copied adjustments",
            'paste_adjustments': "Pasted adjustments",
            'enable_crop': "Crop enabled",
            'disable_crop': "Crop cancelled",
            'apply_crop': "Crop applied",
            'fullscreen': "Fullscreen toggled",
            'zoom_to_fit': "Zoomed to fit",
            'zoom_100': "Zoomed to 100%",
            'zoom_in': "Zoomed in",
            'zoom_out': "Zoomed out",
            # Workflow macros
            'macro_hero_shot': "Marked as hero shot",
            'macro_selects': "Marked as selects",
            'macro_reject': "Marked as reject",
            'macro_maybe': "Marked as maybe",
            # Filters
            'filter_flagged': "Showing only flagged images",
            'filter_5_stars': "Showing only 5 star images",
            'filter_selects': "Showing selects",
            'filter_rejects': "Showing rejects",
            'show_last_captures': f"Showing last {params.get('count')} captures",
            'clear_filters': "Cleared all filters",
            'show_all': "Showing all images",
            # Technical
            'show_overexposure': "Showing overexposure warning",
            'hide_overexposure': "Hiding overexposure warning",
            'show_histogram': "Showing histogram",
            'hide_histogram': "Hiding histogram",
            # Batch
            'batch_apply_to_flagged': "Applying to flagged images",
            'batch_white_balance': "Syncing white balance",
        }

        return feedback_map.get(action, "Command executed")

    def _speak(self, text):
        """Speak text using OpenAI text-to-speech"""
        if not self.voice_feedback_enabled:
            return

        print(f"[DEBUG] TTS: Starting speech for '{text[:50]}...'")
        try:
            start_time = time.time()

            print(f"[DEBUG] TTS: Calling OpenAI API...")
            # Create speech using OpenAI
            response = self.openai_client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                speed=Config.TTS_SPEED
            )

            elapsed = time.time() - start_time
            print(f"[DEBUG] TTS: API call completed in {elapsed:.2f}s")

            # Check response
            if not hasattr(response, 'content'):
                print(f"[ERROR] TTS: Response has no content attribute. Type: {type(response)}")
                return

            content_size = len(response.content)
            print(f"[DEBUG] TTS: Got response, content size: {content_size} bytes")

            if content_size == 0:
                print(f"[ERROR] TTS: Response content is empty")
                return

            # Save to temporary file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name

            print(f"[DEBUG] TTS: Saved to {temp_path}, playing with afplay...")

            # Play the audio file using afplay (macOS)
            process = subprocess.Popen(
                ['afplay', temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            print(f"[DEBUG] TTS: afplay started (PID: {process.pid})")

            # Clean up temp file after a delay
            threading.Timer(Config.TTS_CLEANUP_DELAY, lambda: Path(temp_path).unlink(missing_ok=True)).start()

        except Exception as e:
            print(f"[ERROR] TTS failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Don't fall back to Mac voice - just fail silently

    def _update_status(self, message="Ready"):
        """Update the app status"""
        # Update title to show status (since we can't use emoji icons)
        if "Listening" in message:
            self.title = "Studio 🎤"
        elif message in ["Ready", "Command executed"]:
            self.title = "Studio"
        else:
            self.title = "Studio ⏳"

        for item in self.menu.values():
            # Skip separator items (they don't have a title attribute)
            if hasattr(item, 'title') and item.title and item.title.startswith("Status:"):
                item.title = f"Status: {message}"
                break

    def undo_last_command(self, _):
        """Undo the last executed command"""
        if not self.last_command:
            rumps.alert("No Command to Undo", "No recent command in history")
            return

        transcribed_text, command = self.last_command

        # Show what will be undone
        rumps.alert(
            "Undo Not Yet Implemented",
            f"Would undo: {transcribed_text}\n\n"
            "This feature requires command-specific undo logic."
        )

    def show_settings(self, _):
        """Show settings dialog"""
        window = rumps.Window(
            message="Enter your OpenAI API key:",
            title="Studio Settings",
            default_text=os.getenv("OPENAI_API_KEY", ""),
            ok="Save",
            cancel="Cancel",
            dimensions=(320, 24)
        )

        response = window.run()

        if response.clicked:
            # Save the API key to .env file
            env_path = Path.cwd() / ".env"
            with open(env_path, 'w') as f:
                f.write(f"OPENAI_API_KEY={response.text}\n")

            rumps.alert("Settings Saved", "Please restart Studio for changes to take effect")

    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            "About Studio",
            "Studio - Voice Assistant for Capture One\n\n"
            "Version 2.1 - June 2026 Update\n\n"
            "Features:\n"
            "• 140+ voice commands across 19 categories\n"
            "• Continuous listening mode\n"
            "• OpenAI TTS voice feedback (nova)\n"
            "• Workflow macros (hero shot, selects, reject, maybe)\n"
            "• Quick review & filtering\n"
            "• Technical checks (exposure, histogram)\n"
            "• Batch operations\n\n"
            "Say 'Studio' followed by your command.\n\n"
            "Powered by OpenAI Whisper & TTS"
        )

    def quit_app(self, _):
        """Quit the application"""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        self.audio.terminate()
        rumps.quit_application()


def main():
    """Main entry point"""
    StudioApp().run()


if __name__ == "__main__":
    main()
