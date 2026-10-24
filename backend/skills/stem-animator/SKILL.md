---
name: stem-animator
description: "Generates pedagogically sound, syntactically valid vertical 9:16 Manim Community Edition animations for STEM concepts with synchronized voiceover scripts and adaptive next-topic pathways."
version: "1.2.0"
license: "MIT"
compatibility: "Manim Community Edition >= 0.18.0"
---

# STEM Animator Agent Skill

This skill instructs an AI model (such as Gemma 4 or Gemini) on how to synthesize pedagogical, programmatic Manim Community Edition animations formatted for 9:16 vertical short-form video (TikTok, YouTube Shorts, mobile learning apps), accompanied by a synchronized voiceover script and intelligent sequential curriculum recommendations.

---

## 1. Pedagogical Principle: Single-Concept Mastery (Under 60 Seconds)

Every animation MUST focus on **exactly one single core STEM concept** and convey it with high user engagement in **35 to 50 seconds** (strictly under 60 seconds). Follow the **4-Beat Narrative Arc**:

1. **Beat 1: The Irresistible Hook & Problem Statement (0.0s – 10.0s)**
   - **Spoken Script:** MUST open with a compelling curiosity gap, surprising fact, or real-world challenge that immediately hooks the viewer (e.g. *"What if you had to find one specific contact among a billion phone numbers? Checking one by one would take years. But what if you could do it in just 30 steps?"*).
   - **Visuals:** Top Header (`y ≈ 5.8` to `6.2`) with concept title in sky blue (`#38BDF8`), and an intuitive subtitle question (`y ≈ 5.0` to `5.3`) in muted slate (`#94A3B8`).

2. **Beat 2: Interactive Model Setup (10.0s – 20.0s)**
   - **Spoken Script:** Directly engage the viewer: *"Notice what happens when we examine this structure..."* or *"Look at the relationship between these components..."*
   - **Visuals:** Center Viewport (`y ≈ 0.5` to `2.2`, safe horizontal `x ∈ [-3.5, 3.5]`). Introduce the primary diagram (e.g. sorted array with values and indices, right-angled triangle, electric circuit diagram, or coordinate curve).

3. **Beat 3: Step-by-Step Mechanism & 'Aha!' Revelations (20.0s – 38.0s)**
   - **Spoken Script:** Walk through 2–3 progressive steps explaining the underlying mechanism step-by-step.
   - **Visuals:** Animate progressive transformations (pointers moving, active elements swapping, discarded halves dimming, side squares expanding). Use distinct visual highlights: `Indicate(..., color="#34D399")`, `Circumscribe`, or `.animate.set_color("#FBBF24")`. Use `self.wait(1.5)` between steps so the audience absorbs each transformation.

4. **Beat 4: The Grand Takeaway & Payoff (38.0s – 48.0s)**
   - **Spoken Script:** Deliver an inspiring concluding sentence reinforcing why this concept matters (e.g. *"And that is how logarithmic time turns an impossible problem into fractions of a second!"*).
   - **Visuals:** Bottom Summary Card (`y ≈ -3.8` to `-5.2`) presenting the key formula, law, or time complexity (e.g. `Time: O(log n)`, `a² + b² = c²`, `V(t) = V₀(1 - e^(-t/RC))`). Hold final frame with `self.wait(2.5)`.

---

## 2. Canvas & Layout Constraints (Vertical 9:16)

Every generated Manim script must configure the vertical canvas at the very top:

```python
from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#0F172A"  # Modern dark slate background
```

### Strict Coordinate Safe Zones
- **Total Canvas:** Width = 9.0 units, Height = 16.0 units.
- **Safe Horizontal Range:** `x ∈ [-3.6, 3.6]`. Do NOT exceed width 7.4 units or visual objects will be cropped on mobile devices.
- **Safe Vertical Range:** `y ∈ [-6.2, 6.2]`.
- **Top Header Zone:** `y = 5.0` to `y = 6.2`.
- **Main Visual Canvas:** `y = -1.5` to `y = 3.5`.
- **Bottom Summary Zone:** `y = -3.8` to `y = -5.8`.

---

## 3. High-Contrast Modern Color Palette

All visual assets must use modern, curated hex colors on the dark `#0F172A` background:
- **Primary Accent / Headers:** `#38BDF8` (Sky Blue)
- **Active / Match / Success:** `#34D399` (Emerald Mint)
- **Pointer / Target / Highlight:** `#FBBF24` (Amber Yellow)
- **Secondary Accent / Contrast:** `#F472B6` (Pink / Magenta)
- **Primary Text:** `#F8FAFC` (Pure Light Slate)
- **Muted Subtext / Inactive:** `#94A3B8` (Cool Grey)
- **Box Fills / Containers:** `#1E293B` (Navy Slate) with stroke `#334155`

---

## 4. Manim Community Edition Code Guardrails

1. **Scene Class Name:** The scene class MUST always be named `StemationScene`:
   ```python
   class StemationScene(Scene):
       def construct(self):
           # Visual storytelling beats
   ```

2. **No LaTeX Compiler Dependency:**
   - Use `Text("...", font_size=...)` instead of `MathTex` or `Tex` to ensure 100% portability without external TeX/dvipng installations.
   - Use clean unicode characters for formulas: `²`, `³`, `√`, `π`, `θ`, `→`, `≤`, `≥`, `≠`, `×`, `÷`, `Δ`, `λ`, `Ω`.
   - Example: `Text("a² + b² = c²", font_size=36, color="#FBBF24")`.

3. **Spatial Management & No Overlaps:**
   - Never overlap text or objects.
   - Group related elements using `VGroup(...)` and position with `.next_to()`, `.arrange()`, or `.move_to()`.
   - Scale groups to fit: `group.scale_to_fit_width(7.2)`.

4. **Timing & Pacing (Under 60 Seconds):**
   - Animation transitions: `run_time=1.0` to `run_time=1.5`.
   - Include `self.wait(1.5)` pauses between beats to let the audience absorb each step in sync with narration.
   - Total scene duration (`self.play` runtimes + `self.wait` intervals) MUST be between **35 and 50 seconds** (strictly under 60 seconds).
   - Always conclude with `self.wait(2.5)` to hold the final resolved frame.

---

## 5. Output Format Specification

The model MUST output ONLY a valid JSON object (no markdown fences, no conversational preface):

```json
{
  "topic": "Name of the STEM concept",
  "narration_script": "Engaging 75-110 word spoken script. MUST open with an irresistible curiosity hook question, directly engage the viewer through the visual steps, and conclude with an inspiring takeaway. Natural read time is 35-50 seconds (strictly under 60 seconds).",
  "manim_code": "# Complete executable Python code defining StemationScene with 35-50s runtime",
  "next_topics": [
    "Logical Next Sequential Concept 1",
    "Logical Next Sequential Concept 2",
    "Logical Next Sequential Concept 3"
  ]
}
```
