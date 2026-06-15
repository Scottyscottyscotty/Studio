# Studio - Voice Assistant for Capture One

## Version 2.1 - June 2026 Update

Studio is a macOS menu bar application that provides hands-free voice control for Capture One Pro. Designed specifically to replace a digital technician on photoshoot sets with continuous listening, voice feedback, and workflow macros.

**✨ New in 2.1:** Upgraded to OpenAI SDK 2.41.0, improved TTS debugging, 5-second recording timeout, better error handling, and centralized configuration.

## 🎯 Core Features

- 🎤 **Continuous Listening Mode** - Always active, true hands-free operation
- 🗣️ **Voice Feedback** - Spoken confirmations so you never look away from the shoot
- ⌨️ **Global Hotkey** - `Option+Space` for instant activation
- 📸 **Workflow Macros** - "Mark as hero shot" executes multi-step workflows
- 👁️ **Quick Review** - "Show only flagged" for instant client presentations
- 🤖 **Natural Language** - Speak naturally, semantic understanding
- ⚡ **140+ Commands** - Comprehensive voice control across 19 categories
- 🔧 **Professional Tools** - Batch operations, technical checks, filtering

## 💬 Example Commands

**90+ voice commands with natural language understanding!**

- "Studio, delete the last 4 images" or "trash that picture"
- "Studio, mark the last image as 5 stars" or "give this photo 4 stars"
- "Studio, label this image as red" or "tag that pic as blue"
- "Studio, select the last 10 photos" or "choose all"
- "Studio, export the current image" or "save these shots"
- "Studio, next image" or "go back"
- "Studio, flag this photo" or "favorite that image"
- "Studio, rotate left" or "flip horizontal"
- "Studio, auto adjust" or "zoom to fit"
- "Studio, copy adjustments" or "show fullscreen"

**See [COMMANDS.md](COMMANDS.md) and [FEATURES.md](FEATURES.md) for complete documentation!**

## 🎬 Digital Tech Features

### Continuous Listening Mode
Enable true hands-free operation - no more clicking to activate. Perfect for tethered shooting.

### Voice Feedback
Hear "Marked as hero shot" or "Deleted 4 images" - keep your eyes on the shoot, not the screen.

### Workflow Macros
- **"Mark as hero shot"** → 5 stars + green label + flag
- **"Mark as selects"** → 4 stars + flag
- **"Mark as reject"** → Reject status
- **"Mark as maybe"** → 3 stars + yellow label

### Quick Review
- **"Show only flagged"** → Display selects for client
- **"Show 5 stars"** → Hero shots only
- **"Show last 20 captures"** → Recent work
- **"Clear filters"** → Back to full gallery

### Global Hotkey
Press `Option+Space` anywhere to activate listening - fastest way to issue commands.

**See [FEATURES.md](FEATURES.md) for complete digital tech guide!**

## 📋 Requirements

- **macOS 12.0 or later**
- **Python 3.9 or later** (Python 3.13+ recommended)
- **Capture One Pro** (any recent version)
- **OpenAI API key** with Whisper and TTS API access
- **Homebrew** (recommended for easy PortAudio installation)

### Recommended System

- macOS 13.0+ (Ventura or later)
- Python 3.13+
- Capture One 16.x
- Microphone with good quality (built-in Mac mic works fine)

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

**Studio now supports 90+ voice commands across 15 categories with flexible natural language understanding!**

### Command Categories

1. **Delete** - Remove images with natural phrases
2. **Rating** - 1-5 star ratings with semantic flexibility
3. **Color Labels** - 7 colors (red, orange, yellow, green, blue, purple, white)
4. **Selection** - Multiple ways to select images
5. **Export** - Save images in various ways
6. **Adjustments** - Exposure, contrast, saturation, auto-adjust, reset
7. **Navigation** - Next, previous, first, last image
8. **Flag** - Mark favorites
9. **Reject** - Mark bad images
10. **Crop** - Full crop workflow
11. **Rotation** - Rotate and flip
12. **Copy/Paste** - Transfer settings between images
13. **View** - Fullscreen, zoom controls
14. **Comparison** - Before/after views
15. **Focus** - Focus mask display

### Natural Language Examples

Studio understands natural variations - say it your way:
- "delete" = remove, trash, discard, get rid of
- "image" = photo, picture, shot, pic
- "this/that/these/those" = current, selected
- "increase" = raise, boost, bump up, turn up
- "flag" = star, favorite, fav

### Complete Command Reference

For the full list of all commands and their variations, see **[COMMANDS.md](COMMANDS.md)**

### Quick Examples by Category

**Delete:** "trash that picture", "remove the last 3 photos"
**Rating:** "give this 5 stars", "rate last image as 4 stars"
**Labels:** "tag as blue", "mark this pic red"
**Selection:** "choose all", "pick the last 10 shots"
**Navigation:** "go back", "next", "jump to first image"
**Adjustments:** "auto adjust", "boost exposure by 10"
**View:** "show fullscreen", "zoom to fit"
**Copy/Paste:** "copy adjustments", "paste style"

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
- **OpenAI Whisper API** - Speech-to-text transcription (Whisper-1 model)
- **OpenAI TTS API** - Text-to-speech feedback (TTS-1 model, nova voice)
- **pyaudio** - Audio recording (16kHz mono)
- **AppleScript** - Capture One automation
- **Python 3.9+** - Core application logic

### Voice Pipeline

1. **Audio Capture** → pyaudio records from microphone at 16kHz mono
2. **Transcription** → OpenAI Whisper-1 converts speech to text
3. **Parsing** → Regex-based parser with 140+ patterns
4. **Execution** → AppleScript sends keyboard shortcuts to Capture One
5. **Feedback** → OpenAI TTS-1 speaks confirmation with nova voice at 1.2x speed

### Cost Analysis

Typical usage costs (60 commands/hour):
- **Whisper-1:** ~5 min audio @ $0.006/min = $0.03
- **TTS-1:** ~1,200 characters @ $15/1M = $0.02
- **Total:** ~$0.05 per hour of active use

Very cost-effective for individual photographers!

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

- Verify your API key is correct in `.env` (not `.env.example`!)
- Check you have sufficient API credits at https://platform.openai.com/usage
- Ensure you have access to the Whisper and TTS APIs
- Look for `[DEBUG]` and `[ERROR]` messages in the terminal for details
- API key format should be: `OPENAI_API_KEY=sk-proj-...` (no quotes, no spaces)

### TTS Not Working / Hearing Mac Voice

If you hear the default Mac "Samantha" voice instead of OpenAI's nova voice:
1. Check terminal for `[DEBUG] TTS:` and `[ERROR] TTS` messages
2. Verify your OpenAI API key has TTS API access
3. Check API usage limits at https://platform.openai.com/usage
4. Make sure you're using openai>=2.41.0 (run `pip show openai`)
5. Try regenerating your API key

### No Sound Recording

- Install/reinstall PortAudio: `brew reinstall portaudio`
- Check that your microphone is working in other apps
- Grant microphone permissions in System Preferences

### Commands Timing Out

If recordings end before you finish speaking:
- Edit the timeout in `studio.py` Config class
- Change `MENU_RECORDING_TIMEOUT` and `PROGRAMMATIC_RECORDING_TIMEOUT` (default: 5 seconds)
- Restart Studio after changes

### Dependency Installation Fails

If you have Python 3.13 compatibility issues:
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies one at a time to isolate issues
pip install rumps
pip install openai
pip install pyaudio  # May need: brew install portaudio first
pip install python-dotenv
pip install pyobjc-framework-Cocoa
pip install pynput
```

### Debug Mode

For detailed debugging, watch the terminal output:
- `[DEBUG]` messages show normal operations
- `[ERROR]` messages show failures
- Look for API response times, file sizes, and error tracebacks

## 🛣️ Roadmap

### Completed ✅
- [✅] Continuous listening mode
- [✅] Voice feedback/responses (OpenAI TTS)
- [✅] Batch operations
- [✅] Preset command macros (hero shot, selects, reject, maybe)
- [✅] Keyboard shortcut (Option+Space) - temporarily disabled for Python 3.13 compatibility
- [✅] 140+ commands with natural language understanding

### In Progress 🚧
- [ ] Re-enable global hotkey for Python 3.13
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

### Future Enhancements 🔮
- [ ] Custom wake word support
- [ ] Migration to GPT-Realtime-Whisper for streaming (lower latency)
- [ ] Command confirmation mode for destructive operations
- [ ] Command analytics and workflow insights
- [ ] Integration with other photo editing apps (Lightroom, Photoshop)
- [ ] Packaged .app bundle for easy installation
- [ ] Multi-language support beyond English
- [ ] Cloud sync for command history

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
