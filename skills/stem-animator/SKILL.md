---
name: stem-animator
description: "Generates pedagogically sound, syntactically valid vertical 9:16 Manim Community Edition animations for STEM concepts with synchronized voiceover scripts and next-topic pathways."
version: "1.0.0"
license: "MIT"
compatibility: "Manim Community Edition >= 0.18.0"
---

# STEM Animator Agent Skill

This skill instructs an AI model (such as Gemma 4) on how to generate accurate, programmatic Manim Community Edition animations formatted for 9:16 vertical short-form video (TikTok, YouTube Shorts, mobile learning), accompanied by a concise narration script and intelligent follow-up curriculum recommendations.

---

## 1. Output Format Specification

The model must return a single valid JSON object with the following schema:

```json
{
  "topic": "Name of the concept (e.g. Binary Search)",
  "narration_script": "A concise 25-35 word educational script explaining the core concept intuitively. Read time is roughly 15-20 seconds.",
  "manim_code": "# Valid Python code defining a Manim Scene subclass named StemationScene",
  "next_topics": [
    "Recommended Follow-up Topic 1",
    "Recommended Follow-up Topic 2",
    "Recommended Follow-up Topic 3"
  ]
}
```

---

## 2. Canvas & Layout Constraints (Vertical 9:16)

Every generated Manim script must configure the vertical canvas at the top:

```python
from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#0F172A"  # Modern dark slate background
```

### Safe Coordinate Boundaries
- **X-axis Range:** Safe zone is between `x = -3.8` and `x = 3.8`.
- **Y-axis Range:** Safe zone is between `y = -6.5` and `y = 6.5`.
- **Title Positioning:** Place top-level headers around `y = 6.0`.
- **Main Visual Center:** Place primary diagrams/arrays around `y = 0.5` to `y = 2.0`.
- **Explanation / Formula Area:** Place formulas or step annotations around `y = -3.5` to `y = -5.0`.

---

## 3. High-Contrast Color Palette

Use modern, vibrant hex colors on dark `#0F172A`:
- **Primary Accent / Headers:** `#38BDF8` (Sky Blue)
- **Success / Match / Active:** `#34D399` (Emerald Mint)
- **Warning / Target / Pointer:** `#FBBF24` (Amber Yellow)
- **Secondary / Comparison:** `#F472B6` (Pink / Magenta)
- **Tertiary / Inactive Elements:** `#64748B` (Muted Slate)
- **White / Text:** `#F8FAFC`

---

## 4. Manim Coding Guardrails

1. **Scene Class Name:** The scene class must ALWAYS be named `StemationScene`:
   ```python
   class StemationScene(Scene):
       def construct(self):
           # animation logic
   ```
2. **Robust Text Primitives:**
   - Prefer `Text("...", font_size=...)` instead of `Tex` or `MathTex` if LaTeX might not be present on the host system.
   - For simple math, use unicode symbols in `Text`, e.g., `Text("a² + b² = c²", font_size=36)`.
   - If using `MathTex`, wrap strings cleanly without unescaped LaTeX backslashes.
3. **Pacing & Timing:**
   - The total animation duration (`self.play(...)` and `self.wait(...)`) must be between **15 and 25 seconds** to match the voiceover pace.
   - Use `run_time=1.0` or `1.5` for smooth transitions.
   - Always conclude with `self.wait(2)` so the final frame remains visible.
4. **Clean Animations:**
   - Use `FadeIn`, `Create`, `Transform`, `ReplacementTransform`, `Indicate`, `Circumscribe`, and `FadeOut`.
   - Never overlap objects. Always use `.next_to(...)`, `.shift(...)`, or `VGroup(...).arrange(...)`.

---

## 5. Error Diagnostics & Self-Healing

If the compiler returns an error traceback during rendering, apply these immediate repairs:

| Traceback Pattern | Root Cause | Instant Fix |
|---|---|---|
| `latex: command not found` | Host machine lacks LaTeX compiler | Replace all `MathTex` or `Tex` calls with `Text(...)` and unicode symbols |
| `object has no attribute 'scale_to_fit_width'` | Deprecated method | Use `.scale_to_fit_width(...)` on `Mobject` or `.scale(...)` |
| `KeyError` or `ValueError` in color | Invalid color constant | Replace with hex string like `"#38BDF8"` |
| `Width exceeds frame` | Diagram cut off | Wrap objects in `VGroup` and call `group.scale_to_fit_width(7.0).move_to(ORIGIN)` |
