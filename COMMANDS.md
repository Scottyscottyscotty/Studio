# Studio Voice Commands Reference

This document lists all available voice commands for Studio. Commands are organized by category.

## How to Use Commands

1. Always start with the wake word **"Studio"**
2. Commands are flexible - you can use natural variations
3. Examples: "Studio, delete that image" or "Studio, trash this picture" work the same way

## Command Synonyms

Studio understands natural language variations:
- **delete** = remove, trash, discard, get rid of
- **image** = photo, picture, shot, pic
- **selected/current** = this, that, these, those
- **mark/rate** = set, give, assign
- **label** = tag, mark, color
- **increase** = raise, boost, bump up, turn up, up
- **decrease** = lower, reduce, bring down, turn down, down
- **next** = forward
- **previous** = prev, back, prior
- **flag** = star, favorite, favourite, fav
- **export** = save, output, render
- **select** = choose, pick, highlight, show

---

## Delete Commands

| Command | Example | Description |
|---------|---------|-------------|
| Delete last N images | "delete the last 4 images" | Deletes the last N images |
| Delete selected | "delete this image" | Deletes currently selected image(s) |

**Variations:**
- "Studio, trash that picture"
- "Studio, remove the last 3 photos"
- "Studio, get rid of these shots"

---

## Rating Commands (1-5 Stars)

| Command | Example | Description |
|---------|---------|-------------|
| Rate last image | "mark the last image as 5 stars" | Rate the last image |
| Rate last N images | "rate the last 3 images as 4 stars" | Rate multiple images |
| Rate selected | "give this image 5 stars" | Rate selected image(s) |
| Unrate | "clear rating from this image" | Remove rating (set to 0 stars) |

**Variations:**
- "Studio, set this photo as 4 stars"
- "Studio, assign 5 stars to that shot"
- "Studio, rate this pic as 3 stars"

---

## Color Label Commands

**Available Colors:** red, orange, yellow, green, blue, purple, white

| Command | Example | Description |
|---------|---------|-------------|
| Label last image | "label the last image as red" | Apply color label to last image |
| Label last N images | "tag the last 5 photos as blue" | Apply label to multiple images |
| Label selected | "mark this image as green" | Apply label to selected image(s) |
| Remove label | "clear the color from this image" | Remove color label |

**Variations:**
- "Studio, tag this pic as blue"
- "Studio, color that photo yellow"
- "Studio, mark these images as orange"

---

## Selection Commands

| Command | Example | Description |
|---------|---------|-------------|
| Select by color | "select all images with red label" | Select all images with specific color |
| Select by rating | "select all 5 star images" | Select all images with specific rating |
| Select last N | "select the last 10 images" | Select last N images |
| Select first N | "select the first 5 photos" | Select first N images |
| Select all | "select all" | Select all images |
| Deselect all | "deselect everything" | Clear selection |
| Select flagged | "select all flagged images" | Select all flagged images* |
| Select rejected | "select all rejected photos" | Select all rejected images* |

*Note: Filter-based selections are placeholders and may require manual implementation

**Variations:**
- "Studio, choose all pictures with blue labels"
- "Studio, pick the last 7 shots"
- "Studio, clear selection"

---

## Export Commands

| Command | Example | Description |
|---------|---------|-------------|
| Export selected | "export the current image" | Export selected image(s) |
| Export last N | "export the last 5 images" | Export last N images |
| Export all | "export everything" | Export all images |

**Variations:**
- "Studio, save this photo"
- "Studio, output the last 3 pictures"
- "Studio, render these shots"

---

## Adjustment Commands

### Exposure/Brightness

| Command | Example | Description |
|---------|---------|-------------|
| Increase exposure | "increase the exposure by 10" | Boost exposure* |
| Decrease exposure | "lower the brightness by 5" | Reduce exposure* |

**Variations:**
- "Studio, boost exposure by 15"
- "Studio, turn down the brightness by 20"
- "Studio, bump up exposure by 10"

### Contrast

| Command | Example | Description |
|---------|---------|-------------|
| Increase contrast | "increase the contrast by 10" | Boost contrast* |
| Decrease contrast | "reduce the contrast by 5" | Lower contrast* |

### Saturation

| Command | Example | Description |
|---------|---------|-------------|
| Increase saturation | "increase the saturation by 15" | Boost saturation* |
| Decrease saturation | "lower the saturation by 10" | Reduce saturation* |

### Other Adjustments

| Command | Example | Description |
|---------|---------|-------------|
| Auto adjust | "auto adjust" | Auto-adjust image |
| Reset all | "reset all adjustments" | Reset all edits |

*Note: Fine-grained adjustment controls are placeholders and may require manual implementation

**Variations:**
- "Studio, auto correct"
- "Studio, auto fix"
- "Studio, reset edits"

---

## Navigation Commands

| Command | Example | Description |
|---------|---------|-------------|
| Next image | "next image" | Move to next image |
| Previous image | "previous photo" | Move to previous image |
| Go back | "go back" | Move to previous image |
| Go forward | "forward" | Move to next image |
| First image | "go to the first image" | Jump to first image |
| Last image | "jump to the last photo" | Jump to last image |

**Variations:**
- "Studio, next"
- "Studio, back"
- "Studio, prior photo"

---

## Flag Commands

| Command | Example | Description |
|---------|---------|-------------|
| Flag selected | "flag this image" | Flag/star the current image |
| Unflag selected | "unflag this photo" | Remove flag from image |
| Flag last N | "flag the last 3 images" | Flag multiple images |

**Variations:**
- "Studio, favorite this image"
- "Studio, star that photo"
- "Studio, unstar this picture"

---

## Reject Commands

| Command | Example | Description |
|---------|---------|-------------|
| Reject selected | "reject this image" | Mark image as rejected |
| Unreject selected | "unreject this photo" | Remove reject status |

**Variations:**
- "Studio, trash this image" (marks as rejected, not deleted)
- "Studio, mark as bad"

---

## Crop Commands

| Command | Example | Description |
|---------|---------|-------------|
| Enable crop | "start crop" | Enter crop mode |
| Apply crop | "apply crop" | Apply current crop |
| Cancel crop | "cancel crop" | Exit crop without applying |
| Reset crop | "reset crop" | Undo crop changes |

**Variations:**
- "Studio, begin cropping"
- "Studio, exit crop"
- "Studio, stop cropping"

---

## Rotation Commands

| Command | Example | Description |
|---------|---------|-------------|
| Rotate left | "rotate left" | Rotate 90° counter-clockwise |
| Rotate right | "rotate right" | Rotate 90° clockwise |
| Flip horizontal | "flip horizontal" | Flip image horizontally |
| Flip vertical | "flip vertically" | Flip image vertically |

**Variations:**
- "Studio, rotate counterclockwise"
- "Studio, flip horizontally"

---

## Copy/Paste Style Commands

| Command | Example | Description |
|---------|---------|-------------|
| Copy adjustments | "copy adjustments" | Copy current image settings |
| Paste adjustments | "paste adjustments" | Apply copied settings |

**Variations:**
- "Studio, duplicate edits"
- "Studio, apply settings"
- "Studio, copy style"

---

## View Commands

| Command | Example | Description |
|---------|---------|-------------|
| Enter fullscreen | "show fullscreen" | Enter fullscreen mode |
| Exit fullscreen | "exit fullscreen" | Exit fullscreen mode |
| Zoom to fit | "zoom to fit" | Fit image to screen |
| Zoom 100% | "zoom to 100 percent" | View at 100% size |
| Zoom in | "zoom in" | Zoom in on image |
| Zoom out | "zoom out" | Zoom out from image |

**Variations:**
- "Studio, enter fullscreen"
- "Studio, fit to screen"
- "Studio, zoom to one hundred"

---

## Comparison Commands

| Command | Example | Description |
|---------|---------|-------------|
| Compare | "compare" | Compare images |
| Before/After | "show before and after" | Toggle before/after view |

**Variations:**
- "Studio, show comparison"
- "Studio, view before after"

---

## Focus Commands

| Command | Example | Description |
|---------|---------|-------------|
| Show focus mask | "show focus mask" | Display focus peaking |
| Hide focus mask | "hide focus mask" | Hide focus peaking |

**Variations:**
- "Studio, enable focus mask"
- "Studio, disable focus mask"

---

## Command Count

**Total Commands Implemented:** 90+ command variations

**Fully Implemented Categories:**
- Delete, Rating, Labeling, Selection (basic), Export (basic)
- Navigation, Flag, Reject, Crop, Rotation
- Copy/Paste, View, Comparison, Focus

**Partially Implemented (Placeholders):**
- Filter-based selection (by color/rating/flags)
- Fine-grained adjustment controls (exposure/contrast/saturation values)

---

## Tips for Best Results

1. **Speak clearly** at a normal pace
2. **Always include "Studio"** at the beginning
3. **Use natural language** - the parser understands variations
4. **Be specific** with numbers when needed ("delete the last 4 images")
5. **Wait for confirmation** - you'll get a notification when commands execute

---

## Troubleshooting

If a command doesn't work:
1. Check that Capture One is running and active
2. Verify you're using default keyboard shortcuts
3. Make sure you included the wake word "Studio"
4. Try a different variation of the command
5. Check the console output for error messages
