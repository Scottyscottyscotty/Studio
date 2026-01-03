#!/usr/bin/env python3
"""
Studio - Voice Assistant for Capture One
A macOS menu bar application for voice-controlled photo editing
"""

import rumps
import os
import sys
import threading
import wave
import pyaudio
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from command_parser import CommandParser
from capture_one_controller import CaptureOneController

# Load environment variables
load_dotenv()


class StudioApp(rumps.App):
    def __init__(self):
        super(StudioApp, self).__init__(
            "Studio",
            icon="📷",  # Camera emoji as placeholder, can be replaced with custom icon
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

        self.openai_client = OpenAI(api_key=api_key)

        # Initialize components
        self.command_parser = CommandParser()
        self.capture_one = CaptureOneController()

        # Audio recording settings
        self.is_recording = False
        self.audio_frames = []
        self.audio = pyaudio.PyAudio()

        # Create recordings directory
        self.recordings_dir = Path.home() / ".studio" / "recordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        # Menu items
        self.menu = [
            rumps.MenuItem("Start Listening ⏺", callback=self.toggle_recording),
            rumps.separator,
            rumps.MenuItem("Status: Ready", callback=None),
            rumps.separator,
            rumps.MenuItem("Settings", callback=self.show_settings),
            rumps.MenuItem("About Studio", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

    def toggle_recording(self, sender):
        """Toggle audio recording on/off"""
        if not self.is_recording:
            self.start_recording(sender)
        else:
            self.stop_recording(sender)

    def start_recording(self, sender):
        """Start recording audio"""
        self.is_recording = True
        sender.title = "Stop Listening ⏹"
        self.menu["Status: Ready"].title = "Status: Listening..."
        self.icon = "🎤"

        # Start recording in a separate thread
        threading.Thread(target=self._record_audio, daemon=True).start()

    def stop_recording(self, sender):
        """Stop recording and process the audio"""
        self.is_recording = False
        sender.title = "Start Listening ⏺"
        self.menu["Status: Listening..."].title = "Status: Processing..."
        self.icon = "⏳"

        # Process the recording in a separate thread
        threading.Thread(target=self._process_recording, daemon=True).start()

    def _record_audio(self):
        """Record audio from the microphone"""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        self.audio_frames = []

        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
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
            # Save the recording to a file
            audio_file_path = self.recordings_dir / "temp_recording.wav"

            wf = wave.open(str(audio_file_path), 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()

            # Send to OpenAI Whisper API
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )

            transcribed_text = transcript.text.strip()

            # Parse and execute the command
            if transcribed_text:
                self._execute_command(transcribed_text)
            else:
                self._reset_status("No speech detected")

        except Exception as e:
            rumps.notification(
                "Studio Error",
                "Processing Error",
                str(e)
            )
            self._reset_status("Error occurred")

    def _execute_command(self, transcribed_text):
        """Parse and execute the voice command"""
        try:
            # Parse the command
            command = self.command_parser.parse(transcribed_text)

            if command:
                # Execute the command
                success = self.capture_one.execute(command)

                if success:
                    rumps.notification(
                        "Studio",
                        "Command Executed",
                        f'"{transcribed_text}"'
                    )
                    self._reset_status("Command executed")
                else:
                    rumps.notification(
                        "Studio",
                        "Execution Failed",
                        "Could not execute command in Capture One"
                    )
                    self._reset_status("Execution failed")
            else:
                rumps.notification(
                    "Studio",
                    "Command Not Recognized",
                    f'"{transcribed_text}"'
                )
                self._reset_status("Command not recognized")

        except Exception as e:
            rumps.notification(
                "Studio Error",
                "Command Error",
                str(e)
            )
            self._reset_status("Error occurred")

    def _reset_status(self, message="Ready"):
        """Reset the app status"""
        self.icon = "📷"
        for item in self.menu.values():
            if item.title.startswith("Status:"):
                item.title = f"Status: {message}"
                break

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
            "Version 1.0\n\n"
            "A voice-controlled assistant for professional photo editing.\n\n"
            "Say 'Studio' followed by your command to control Capture One."
        )

    def quit_app(self, _):
        """Quit the application"""
        self.audio.terminate()
        rumps.quit_application()


def main():
    """Main entry point"""
    StudioApp().run()


if __name__ == "__main__":
    main()
