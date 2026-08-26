# Studio Architecture Review - First Principles

**Date:** June 15, 2026  
**Current State:** 2,455 lines of code  
**Question:** Are we overcomplicating this?

---

## 🔍 Current Architecture Analysis

### Code Breakdown
```
studio.py                 714 lines   Menu bar app, audio, API calls
command_parser.py         648 lines   140+ regex patterns  ← COMPLEX
capture_one_controller.py 832 lines   AppleScript execution
utils.py                  153 lines   Helper functions
debug_capture_one.py      108 lines   Diagnostic tool
─────────────────────────────────────
TOTAL:                   2455 lines
```

### Current Flow
```
User speaks
    ↓
PyAudio records (5 second timeout)
    ↓
Save to WAV file
    ↓
OpenAI Whisper API → "Studio mark this image 3 stars"
    ↓
Regex Parser (648 lines, 140+ patterns) → {action: 'rate_selected', rating: 3}
    ↓
AppleScript Controller → keystroke "3"
    ↓
Capture One (all selected images get rated)
```

---

## 🎯 What's Working Well

✅ **Audio Pipeline:** PyAudio → Whisper works great  
✅ **TTS Feedback:** OpenAI nova voice is perfect  
✅ **Menu Bar UI:** Simple and functional  
✅ **AppleScript:** Actually works (permissions issue is user-side)  

---

## 🚨 What's Overcomplicated

### 1. **648 Lines of Regex Patterns** ← BIGGEST ISSUE

**Current approach:**
```python
# 140+ patterns like this:
{
    'pattern': rf'{self._s("mark")}\s+(?:the\s+)?{self._s("selected")}\s+{self._s("image")}\s+(?:as\s+)?(\d+)\s+star',
    'action': 'rate_selected',
    'params': lambda m: {'rating': int(m.group(1))}
},
{
    'pattern': rf'{self._s("mark")}\s+(?:the\s+)?last\s+{self._s("image")}\s+(?:as\s+)?(\d+)\s+star',
    'action': 'rate_last',
    'params': lambda m: {'count': 1, 'rating': int(m.group(1))}
},
# ... 138 more patterns ...
```

**Problems:**
- Hard to maintain (changing one synonym breaks 20 patterns)
- Fragile (typos, variations break everything)
- No context awareness
- No learning from corrections
- Massive code duplication

---

## 💡 Modern Alternatives (2026)

### Option A: **GPT-4 with Function Calling** (RECOMMENDED)

**New architecture:**
```
User speaks
    ↓
Whisper → "Studio mark this image 3 stars"
    ↓
GPT-4 with function calling (3-4 lines of code!)
    ↓
{action: 'rate_selected', rating: 3}
    ↓
Execute in Capture One
```

**Code reduction:** 648 lines → ~50 lines  
**Cost:** +$0.01 per command (still only $0.06/hour total)  
**Benefits:**
- ✅ Natural language understanding
- ✅ Handles typos, variations automatically
- ✅ Context-aware ("this", "that", "these")
- ✅ Can learn from corrections
- ✅ No regex maintenance hell

**Example implementation:**
```python
def parse_command(text: str) -> dict:
    """Use GPT-4 to parse natural language into structured command"""
    
    functions = [{
        "name": "execute_capture_one_command",
        "description": "Execute a command in Capture One Pro",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["rate", "label", "delete", "export", "select", "flag", "rotate"]
                },
                "target": {
                    "type": "string",
                    "enum": ["selected", "last", "first", "all"],
                    "description": "Which image(s) to act on"
                },
                "value": {
                    "type": "integer",
                    "description": "Rating (1-5), count, or amount"
                }
            },
            "required": ["action", "target"]
        }
    }]
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",  # Fast & cheap
        messages=[{"role": "user", "content": text}],
        functions=functions,
        function_call={"name": "execute_capture_one_command"}
    )
    
    return json.loads(response.choices[0].message.function_call.arguments)

# That's it! Replaces 648 lines of regex.
```

---

### Option B: **Structured Outputs** (SIMPLER)

Even simpler with OpenAI's new structured outputs:

```python
from pydantic import BaseModel

class CaptureOneCommand(BaseModel):
    action: str  # "rate", "label", "delete", etc.
    target: str  # "selected", "last N", "all"
    value: int | None  # Rating, count, or None

def parse_command(text: str) -> CaptureOneCommand:
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Parse Capture One voice commands into structured format"
        }, {
            "role": "user",
            "content": text
        }],
        response_format=CaptureOneCommand
    )
    return response.choices[0].message.parsed

# Even simpler! Just ~10 lines.
```

---

### Option C: **Hybrid Approach** (BALANCED)

Keep simple commands as patterns, use GPT-4 for complex ones:

```python
# Simple patterns (20 lines instead of 648)
SIMPLE_PATTERNS = {
    r'delete': {'action': 'delete', 'target': 'selected'},
    r'next': {'action': 'navigate', 'direction': 'next'},
    r'flag': {'action': 'flag', 'target': 'selected'},
    # ... ~15 more
}

# Fallback to GPT-4 for complex parsing
def parse_command(text: str) -> dict:
    for pattern, cmd in SIMPLE_PATTERNS.items():
        if re.search(pattern, text, re.I):
            return cmd
    
    # Use GPT-4 for complex commands
    return gpt4_parse(text)
```

---

## 🎛️ Other Simplifications

### 2. **Fixed Timeout → Voice Activity Detection**

**Current:** 5 second fixed timeout (too long for quick commands, too short for slow speakers)

**Better:**
```python
import webrtcvad

vad = webrtcvad.Vad(2)  # Sensitivity level

# Stop recording 1 second after user stops speaking
# Start processing immediately when done
# More natural, faster, no cut-offs
```

**Code:** ~30 lines  
**Benefit:** Better UX, faster processing

---

### 3. **AppleScript → Accessibility API** (MAYBE)

**Current:** 832 lines of AppleScript wrappers

**Alternative:** Use macOS Accessibility API directly via PyObjC
```python
from ApplicationServices import AXUIElementCreateApplication, AXUIElementPerformAction

# More direct control
# Faster execution
# Better error handling
```

**But:** AppleScript actually works fine. Only optimize if needed.

---

## 📊 Proposed New Architecture

### **Minimal Studio v3.0**

```
┌─────────────────────────────────────────────┐
│           studio.py (~200 lines)            │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ PyAudio      │  │ OpenAI Client    │   │
│  │ Recording    │  │ Whisper + GPT-4  │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
                    ↓
        GPT-4 Function Calling (~50 lines)
                    ↓
┌─────────────────────────────────────────────┐
│    capture_one.py (~150 lines)              │
│    Simple AppleScript executor               │
└─────────────────────────────────────────────┘

TOTAL: ~400 lines (vs 2,455 current)
```

---

## 💰 Cost Analysis

### Current Approach
- Whisper: $0.006/min
- TTS: $15/1M chars
- **Total: $0.05/hour**

### With GPT-4o-mini for parsing
- Whisper: $0.006/min
- GPT-4o-mini: $0.15/1M input tokens (~50 tokens per command = $0.0000075)
- TTS: $15/1M chars
- **Total: $0.06/hour** (just $0.01 more!)

**Verdict:** Worth it for 90% code reduction!

---

## 🚀 Recommended Path Forward

### **Option 1: Revolutionary (Clean Slate)**
- Start fresh with GPT-4 function calling
- 400 lines total
- Modern architecture
- **Effort:** 4-6 hours
- **Risk:** Medium (new codebase)

### **Option 2: Evolutionary (Gradual)**
- Keep current architecture
- Replace command_parser.py with GPT-4 function calling
- Keep everything else the same
- **Effort:** 1-2 hours
- **Risk:** Low (minimal changes)

### **Option 3: Hybrid**
- Simple commands → regex (20 patterns)
- Complex commands → GPT-4
- Best of both worlds
- **Effort:** 2-3 hours
- **Risk:** Low

---

## 🎯 My Recommendation

**Go with Option 2: Evolutionary**

**Why:**
1. ✅ Minimal risk (only replacing parser)
2. ✅ Immediate benefit (648 lines → 50 lines)
3. ✅ Easy to rollback
4. ✅ Basically free ($0.01/hour increase)
5. ✅ Better accuracy (GPT-4 understands context)

**Implementation:**
1. Create `command_parser_gpt.py` (new file, ~50 lines)
2. Swap `self.command_parser = CommandParser()` → `GPT4CommandParser()`
3. Test with your workflow
4. Keep old parser as fallback
5. If it works → delete 648 lines of regex!

---

## 🔧 Specific Issue: "mark this image 3 stars"

**Current problem:**
- Whisper: ✓ "Studio mark this image 3 stars"
- Parser: ✓ {action: 'rate_selected', rating: 3}
- AppleScript: ✓ keystroke "3"
- Capture One: ✗ **All selected images got rated**

**Root cause:** Capture One behavior, not code

**Two solutions:**

### Solution A: Better targeting
```applescript
-- Ensure only ONE image is selected first
tell application "System Events"
    tell process "Capture One"
        -- Press Escape to deselect all
        keystroke (ASCII character 27)
        delay 0.1
        -- Selected image is now the "primary" one
        keystroke "3"
    end tell
end tell
```

### Solution B: GPT-4 context awareness
```python
# GPT-4 can understand:
"mark THIS image 3 stars"      → target: "primary_selected"
"mark THESE images 3 stars"    → target: "all_selected"
"mark the LAST image 3 stars"  → target: "last"

# Regex can't distinguish "this" vs "these"
# GPT-4 understands the intent naturally
```

---

## 📝 Next Steps

**Want to simplify?**

1. **Tell me which option you prefer:**
   - Option 1: Clean slate (~400 lines total)
   - Option 2: Just replace parser (low risk)
   - Option 3: Hybrid approach

2. **I'll implement it** (should take 1-2 hours)

3. **We test together**

4. **Delete old complex code** 🎉

---

**Bottom line:** Yes, we're overcomplicating it. GPT-4 function calling makes this WAY simpler. Want me to build it?
