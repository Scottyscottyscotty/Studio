# Studio - Voice Assistant for Capture One

Studio is a macOS menu bar application that provides voice control for Capture One Pro. Control your photo editing workflow with natural language voice commands!

## 🎯 Features

- 🎤 **Voice-activated commands** - Just say "Studio" and give your command
- 📍 **Menu bar integration** - Small, unobtrusive icon in your macOS menu bar
- 🤖 **Natural language processing** - Speak naturally, no need to memorize exact phrases
- ⚡ **Fast and responsive** - Commands execute immediately in Capture One
- 🔧 **Extensible** - Easy to add new commands and customize behavior

## 💬 Example Commands

- "Studio, delete the last 4 images"
- "Studio, mark the last image as 5 stars"
- "Studio, rate the last 3 images as 4 stars"
- "Studio, label this image as red"
- "Studio, select all images with red labels"
- "Studio, export the current image"
- "Studio, next image"
- "Studio, flag this photo"
- "Studio, increase the exposure by 10"

## 📋 Requirements

- **macOS 12.0 or later**
- **Python 3.8 or later**
- **Capture One Pro** (any recent version)
- **OpenAI API key** with Whisper API access
- **Homebrew** (recommended for easy PortAudio installation)

## 🚀 Installation

### Quick Setup

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd Studio
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Add your OpenAI API key:**
   - The setup script will prompt you to edit the `.env` file
   - Get your API key from: https://platform.openai.com/api-keys
   - Add it to the `.env` file:
     ```
     OPENAI_API_KEY=sk-your-api-key-here
     ```

4. **Launch Studio:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

### Manual Setup

If you prefer to set up manually:

1. **Install PortAudio:**
   ```bash
   brew install portaudio
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run Studio:**
   ```bash
   python3 studio.py
   ```

## 🎮 Usage

1. **Launch Studio** - The camera emoji 📷 will appear in your menu bar
2. **Start listening** - Click the icon and select "Start Listening ⏺"
3. **Give a command** - Say "Studio" followed by your command
4. **Watch it execute** - The command will be executed in Capture One

### Tips

- Make sure Capture One is running before giving commands
- Speak clearly and at a normal pace
- Always start commands with "Studio"
- The app will show a microphone emoji 🎤 while listening
- You'll get a notification when the command is executed

## 📝 Supported Commands

### Rating Commands
- "Mark/rate/set the last image as [1-5] stars"
- "Rate the last [N] images as [1-5] stars"
- "Rate this image as [1-5] stars"

### Color Label Commands
- "Label/mark/tag this image as [color]"
- "Label the last [N] images as [color]"
- Colors: red, orange, yellow, green, blue, purple, white

### Selection Commands
- "Select all images with [color] label"
- "Select all [1-5] star images"
- "Select the last [N] images"
- "Select all"
- "Deselect all"

### Delete Commands
- "Delete the last [N] images"
- "Delete the current/selected image"

### Export Commands
- "Export the current/selected images"
- "Export the last [N] images"

### Navigation Commands
- "Next image"
- "Previous image"

### Flag Commands
- "Flag this image"
- "Unflag this image"
- "Reject this image"

### Crop Commands
- "Enable/start crop"
- "Apply crop"
- "Cancel/disable crop"

### Adjustment Commands
- "Increase/raise/boost the exposure by [N]"
- "Decrease/lower/reduce the exposure by [N]"
- "Reset all adjustments"

## ⚙️ Configuration

### API Key Management

You can update your OpenAI API key through the menu:
1. Click the Studio icon in the menu bar
2. Select "Settings"
3. Enter your new API key
4. Restart Studio

### Customizing Commands

To add or modify commands, edit `command_parser.py`:

```python
# Add a new pattern to the patterns list
{
    'pattern': r'your regex pattern here',
    'action': 'your_action_name',
    'params': lambda m: {'param': 'value'}
}
```

Then implement the action in `capture_one_controller.py`.

### Keyboard Shortcuts

Default Capture One shortcuts are used. If you've customized your shortcuts, you may need to update them in `capture_one_controller.py`.

## 🏗️ Architecture

Studio is built with:
- **rumps** - macOS menu bar application framework
- **OpenAI Whisper API** - Speech-to-text transcription
- **pyaudio** - Audio recording
- **AppleScript** - Capture One automation
- **Python 3** - Core application logic

### Project Structure

```
Studio/
├── studio.py                    # Main application and menu bar UI
├── command_parser.py            # Natural language command parsing
├── capture_one_controller.py   # Capture One automation via AppleScript
├── utils.py                     # Utility functions (version detection, etc.)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── setup.sh                     # Installation script
├── run.sh                       # Launch script
└── README.md                    # This file
```

## 🔧 Troubleshooting

### Microphone Permission Denied

If you get a microphone permission error:
1. Open System Preferences → Security & Privacy → Privacy → Microphone
2. Make sure Python or Terminal has microphone access enabled

### Capture One Commands Not Working

- Make sure Capture One is running and active
- Check that you're using default keyboard shortcuts
- Verify the correct Capture One version is detected (check console output)

### OpenAI API Errors

- Verify your API key is correct in `.env`
- Check you have sufficient API credits
- Ensure you have access to the Whisper API

### No Sound Recording

- Install/reinstall PortAudio: `brew reinstall portaudio`
- Check that your microphone is working in other apps
- Grant microphone permissions in System Preferences

## 🛣️ Roadmap

Future enhancements planned:
- [ ] Custom wake word support
- [ ] Continuous listening mode
- [ ] Voice feedback/responses
- [ ] Batch operations
- [ ] Preset command macros
- [ ] Integration with other photo editing apps
- [ ] Keyboard shortcut for quick activation
- [ ] Packaged .app bundle for easy installation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project however you'd like!

## 🙏 Acknowledgments

- OpenAI for the Whisper API
- Capture One for their excellent photo editing software
- The Python community for amazing tools and libraries

## 📞 Support

Having issues? Please open an issue on GitHub with:
- Your macOS version
- Capture One version
- Error messages or logs
- Steps to reproduce the problem

---

**Made with ❤️ for photographers who want to work faster**
