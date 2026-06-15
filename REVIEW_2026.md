# Studio Voice Assistant - 2026 Review & Improvement Plan

**Review Date:** June 15, 2026  
**Last Updated:** Several months ago  
**Current Status:** Working but using outdated dependencies

---

## Executive Summary

Studio is a voice-controlled assistant for Capture One Pro with 140+ commands. The core functionality works, but it's using severely outdated OpenAI SDK (v1.40.0 from ~2024) while the current version is v2.41.0 (June 2026). OpenAI has released new Realtime API models, but for Studio's command-based use case, the traditional Whisper + TTS approach remains the most cost-effective solution.

---

## Current Architecture Analysis

### Voice Pipeline
1. **Input:** pyaudio records from microphone (16kHz mono)
2. **STT:** OpenAI Whisper-1 API (request/response)
3. **Parsing:** Regex-based command parser with 140+ patterns
4. **Execution:** AppleScript automation of Capture One
5. **Feedback:** OpenAI TTS-1 API (nova voice, 1.2x speed)

### Known Issues
- ✅ **SDK Version:** Using openai==1.40.0 (18+ months outdated)
- ✅ **TTS Failing:** Silent failures, falling back to Mac voice
- ⚠️ **Menu Timeout:** Still 10 seconds (user wanted 5 seconds)
- ⚠️ **Python 3.13 Compatibility:** pynput hotkey disabled
- ⚠️ **No Tests:** Zero test coverage
- ⚠️ **No CI/CD:** No automated build/test pipeline

---

## OpenAI API Landscape (2026)

### Available Voice Models

| Model | Type | Best For | Cost | Latency |
|-------|------|----------|------|---------|
| **GPT-Realtime-2** | Speech-to-speech | Conversational AI agents | $32/1M input tokens | Ultra-low |
| **GPT-Realtime-Whisper** | Streaming STT | Real-time transcription | $0.017/min | Low |
| **Whisper-1** | Batch STT | File transcription | $0.006/min | Medium |
| **TTS-1** | Text-to-speech | Voice synthesis | $15/1M chars | Medium |

### Recommendation for Studio

**KEEP CURRENT APPROACH** (Whisper-1 + TTS-1) because:
- ✅ Studio is command-based, not conversational
- ✅ Most cost-effective for discrete commands
- ✅ No need for GPT-5-class reasoning
- ✅ User is individual photographer, not enterprise
- ✅ Current architecture works, just needs modernization

**UPGRADE PATH:**
1. **Phase 1 (Now):** Upgrade to latest SDK, fix bugs
2. **Phase 2 (Future):** Optionally migrate to GPT-Realtime-Whisper for streaming (lower latency)
3. **Phase 3 (Maybe):** Consider GPT-Realtime-2 if adding conversational features

---

## Recommended Improvements

### Priority 1: Critical Updates

#### 1.1 Upgrade OpenAI SDK
```python
# Current
openai==1.40.0
httpx==0.25.2

# Recommended
openai>=2.41.0  # Latest as of June 2026
# Remove httpx pin - latest SDK handles this
```

**Benefits:**
- Python 3.13 compatibility
- Better error handling
- TTS improvements (likely fixes silent failures)
- Security patches
- Performance improvements

#### 1.2 Fix Menu Recording Timeout
```python
# Line 187: Change from 10 to 5 seconds
threading.Timer(5.0, self._auto_stop_menu_recording).start()
```

#### 1.3 Improve TTS Error Handling
Add comprehensive logging to diagnose why TTS fails:
```python
def _speak(self, text):
    if not self.voice_feedback_enabled:
        return
    
    print(f"[DEBUG] TTS: Starting speech for '{text}'")
    try:
        print(f"[DEBUG] TTS: Calling OpenAI API...")
        response = self.openai_client.audio.speech.create(...)
        print(f"[DEBUG] TTS: Got response, content size: {len(response.content)} bytes")
        # ... rest of implementation
    except Exception as e:
        print(f"[ERROR] TTS failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
```

### Priority 2: Code Quality

#### 2.1 Add Type Hints
```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def _process_recording(self) -> None:
    """Process the recorded audio through Whisper API"""
    
def _execute_command(self, transcribed_text: str) -> None:
    """Parse and execute the voice command"""
```

#### 2.2 Configuration Management
Create `config.py`:
```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AudioConfig:
    CHUNK_SIZE: int = 1024
    FORMAT: int = pyaudio.paInt16
    CHANNELS: int = 1
    SAMPLE_RATE: int = 16000
    RECORDING_TIMEOUT: int = 5

@dataclass
class APIConfig:
    WHISPER_MODEL: str = "whisper-1"
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "nova"
    TTS_SPEED: float = 1.2
    API_TIMEOUT: float = 30.0
```

#### 2.3 Better Error Recovery
```python
def _process_recording(self):
    """Process with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # ... existing code
            break
        except openai.APIConnectionError as e:
            if attempt < max_retries - 1:
                print(f"[DEBUG] Retry {attempt + 1}/{max_retries} after connection error")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### Priority 3: Features

#### 3.1 Re-enable Global Hotkey
Fix pynput Python 3.13 compatibility or switch to alternative:
```python
# Option A: Update pynput to latest version
pynput>=1.7.7  # Check for Python 3.13 support

# Option B: Use PyObjC directly (macOS-specific)
from Cocoa import NSEvent
# Implement hotkey using NSEvent.addGlobalMonitorForEventsMatchingMask
```

#### 3.2 Add Command Confirmation Mode
For destructive commands, add voice confirmation:
```python
def _needs_confirmation(self, command: Command) -> bool:
    """Check if command needs user confirmation"""
    destructive_actions = ['delete_last', 'delete_selected', 'batch_apply_to_flagged']
    return command.action in destructive_actions

def _confirm_command(self, command: Command) -> bool:
    """Get voice confirmation for destructive commands"""
    self._speak("Are you sure?")
    # Record 2-second response
    # Parse for "yes", "confirm", "do it", etc.
```

#### 3.3 Command History & Analytics
```python
import json
from datetime import datetime

def _save_command_history(self):
    """Save command history to disk for analytics"""
    history_file = Path.home() / ".studio" / "history.jsonl"
    with history_file.open('a') as f:
        for text, command in self.command_history:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'action': command.action,
                'params': command.params
            }
            f.write(json.dumps(entry) + '\n')
```

### Priority 4: Testing

#### 4.1 Unit Tests
```python
# tests/test_command_parser.py
import pytest
from command_parser import CommandParser

def test_parse_rating_with_digits():
    parser = CommandParser()
    cmd = parser.parse("Studio mark this 5 stars")
    assert cmd.action == 'rate_selected'
    assert cmd.params['rating'] == 5

def test_parse_rating_with_words():
    parser = CommandParser()
    cmd = parser.parse("Studio mark this five stars")
    assert cmd.action == 'rate_selected'
    assert cmd.params['rating'] == 5
```

#### 4.2 Integration Tests
```python
# tests/test_studio_integration.py
def test_full_pipeline_mock():
    """Test full pipeline with mocked OpenAI calls"""
    # Mock Whisper response
    # Mock TTS response
    # Verify command execution
```

### Priority 5: Documentation

#### 5.1 Update README
- Add Python 3.13 requirement
- Update installation instructions
- Add troubleshooting section
- Add performance benchmarks

#### 5.2 API Documentation
Generate docs with pdoc or sphinx:
```bash
pip install pdoc
pdoc studio.py command_parser.py capture_one_controller.py -o docs/
```

---

## Migration Plan

### Phase 1: Immediate (1-2 hours)
1. ✅ Upgrade OpenAI SDK to 2.41.0
2. ✅ Fix menu timeout (10s → 5s)
3. ✅ Add comprehensive TTS debugging
4. ✅ Test end-to-end on Mac
5. ✅ Commit and push fixes

### Phase 2: Short-term (1 week)
1. Add type hints throughout
2. Create configuration module
3. Add basic unit tests
4. Fix or replace pynput for Python 3.13
5. Update documentation

### Phase 3: Medium-term (1 month)
1. Add command confirmation mode
2. Implement command analytics
3. Add integration tests
4. Set up CI/CD pipeline
5. Consider GPT-Realtime-Whisper for streaming

---

## Cost Analysis

### Current Usage (Whisper-1 + TTS-1)
- **Whisper-1:** $0.006/min
- **TTS-1:** $15/1M characters

**Typical Session (1 hour):**
- 60 commands @ 5 seconds each = 5 minutes audio
- Whisper: 5 min × $0.006 = $0.03
- TTS: 60 responses @ 20 chars = 1,200 chars = $0.018
- **Total: ~$0.05 per hour**

### Alternative: GPT-Realtime-Whisper
- $0.017/min streaming
- **Total: $1.02 per hour** (20x more expensive)

### Alternative: GPT-Realtime-2
- $32/1M audio tokens (complex pricing)
- **Estimated: $5-10 per hour** (100-200x more expensive)

**Conclusion:** Current approach is optimal for Studio's use case.

---

## Sources & References

- [OpenAI Realtime API Overview](https://openai.com/index/introducing-gpt-realtime/)
- [GPT-Realtime-2 vs Whisper Comparison](https://www.mindstudio.ai/blog/gpt-realtime-2-vs-translate-vs-whisper-comparison)
- [OpenAI Python SDK Changelog](https://platform.openai.com/docs/changelog)
- [OpenAI Voice Models Explained](https://www.mindstudio.ai/blog/gpt-realtime-voice-models-explained)
- [Advancing Voice Intelligence - OpenAI](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)

---

## Next Steps

**Immediate Action Items:**
1. Upgrade dependencies
2. Fix timeout bug
3. Debug TTS failures
4. Test on Mac with Capture One

**Questions for User:**
1. Do you want command confirmation for destructive actions?
2. Should we track command analytics for workflow optimization?
3. Is the current response time acceptable, or worth paying for streaming?
4. Any new Capture One features or commands to add?

---

**Generated:** June 15, 2026  
**By:** Claude Code Review
