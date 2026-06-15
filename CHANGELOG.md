# Changelog

All notable changes to Studio Voice Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-06-15

### 🚀 Major Updates

#### Upgraded OpenAI SDK
- **BREAKING:** Upgraded from openai 1.40.0 to >=2.41.0 (18+ months of updates)
- Removed httpx version pin (now handled by latest SDK)
- Updated pynput to >=1.7.7 for Python 3.13 compatibility
- Full Python 3.9-3.13 support

#### Configuration System
- Added centralized `Config` class for all application settings
- All hardcoded values moved to Config constants
- Easy customization of timeouts, models, and audio parameters
- Version tracking in code: `Config.VERSION = "2.1"`

### ✨ Features

#### Recording Improvements
- Reduced menu recording timeout from 10s to 5s (user feedback)
- Standardized programmatic recording to 5s
- Both timeouts now configurable via `Config` class

#### Enhanced TTS Debugging
- Comprehensive debug logging for TTS pipeline
- Tracks API call duration, response size, and playback status
- Full exception tracebacks for easier troubleshooting
- Removed silent fallback to Mac voice (now logs errors instead)
- Shows afplay process ID for audio playback verification

### 🔧 Improvements

#### Code Quality
- Moved all imports to top of file (tempfile, time)
- Removed inline imports for better performance
- Centralized audio configuration (chunk size, sample rate, format, channels)
- Centralized API configuration (models, timeouts, voice settings)
- Better constant naming and organization

#### Documentation
- Created comprehensive REVIEW_2026.md with:
  - OpenAI API landscape analysis (Realtime vs Whisper/TTS)
  - Cost comparison and recommendations
  - Architecture review and improvement roadmap
  - Migration plan (Phase 1-3)
  - Sources and references
- Updated README.md with:
  - Version 2.1 announcement
  - Python 3.13 requirements
  - Expanded troubleshooting section
  - Cost analysis ($0.05/hour)
  - Voice pipeline diagram
  - Completed/in-progress roadmap items
- Updated About dialog:
  - Now shows "Version 2.1 - June 2026 Update"
  - Lists 140+ commands (was 90+)
  - Mentions all feature categories
  - Credits OpenAI Whisper & TTS

### 🐛 Bug Fixes

- Fixed inconsistent timeout messaging (now correctly shows 5 seconds)
- Fixed TTS error handling (no longer silently fails)
- Improved API error visibility with timestamps and durations

### 📊 Technical Details

#### OpenAI API Updates Incorporated
As of June 2026, OpenAI has released:
- GPT-Realtime-2: Speech-to-speech with GPT-5-class reasoning
- GPT-Realtime-Translate: Live translation across 70+ languages  
- GPT-Realtime-Whisper: Streaming STT ($0.017/min)

**Studio Decision:** Keeping Whisper-1 + TTS-1 approach because:
- 20x cheaper than streaming alternatives
- Studio is command-based, not conversational
- No need for GPT-5-class reasoning
- Current architecture is optimal for discrete commands
- Individual photographer use case (not enterprise)

### 🔍 Known Issues

- Global hotkey (Option+Space) still disabled pending Python 3.13 pynput fix
- No automated tests yet (planned for Phase 2)
- TTS may fail silently on some API configurations (check terminal for errors)

### 📦 Dependencies

```
rumps==0.4.0
openai>=2.41.0
pyaudio==0.2.14
python-dotenv==1.0.0
pyobjc-framework-Cocoa==10.1
pynput>=1.7.7
```

### 🔄 Migration Guide

#### From v2.0 to v2.1

1. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Verify API key:**
   Make sure `.env` file exists (not just `.env.example`) with your OpenAI key

3. **Check terminal output:**
   New version has extensive debug logging - watch for `[DEBUG]` and `[ERROR]` messages

4. **Test TTS:**
   If you hear Mac voice instead of OpenAI voice, check API key has TTS access

5. **Adjust timeouts (optional):**
   If 5 seconds is too short/long, edit `Config.MENU_RECORDING_TIMEOUT` in studio.py

### 💰 Cost Impact

**No change in API costs:**
- Still using Whisper-1 and TTS-1
- Same pricing: ~$0.05 per hour of active use
- Newer SDK may have better efficiency, potentially reducing costs slightly

---

## [2.0.0] - Previous Release

### Features
- Initial release with 140+ commands across 19 categories
- Continuous listening mode
- Voice feedback with Mac TTS
- Workflow macros (hero shot, selects, reject, maybe)
- Quick review and filtering
- Technical checks (exposure, histogram)
- Batch operations
- Natural language understanding with semantic synonyms
- AppleScript-based Capture One automation

### Known Issues
- Using outdated OpenAI SDK 1.40.0
- TTS falling back to Mac voice
- 10-second timeout too long
- No centralized configuration
- Limited error visibility

---

## Sources & References

### June 2026 Research
- [OpenAI Realtime API](https://openai.com/index/introducing-gpt-realtime/)
- [GPT-Realtime-2 vs Whisper Comparison](https://www.mindstudio.ai/blog/gpt-realtime-2-vs-translate-vs-whisper-comparison)
- [OpenAI Voice Models Explained](https://www.mindstudio.ai/blog/gpt-realtime-voice-models-explained)
- [Advancing Voice Intelligence](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
- [OpenAI Python SDK](https://pypi.org/project/openai/)

---

**Last Updated:** June 15, 2026  
**Maintained By:** Claude Code
