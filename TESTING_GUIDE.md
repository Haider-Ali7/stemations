# 🚀 Stemations - Run & Testing Guide

This comprehensive guide walks you through running, testing, and demonstrating **Stemations** from end to end.

---

## 📋 Table of Contents
1. [Prerequisites & Verification](#1-prerequisites--verification)
2. [Step 1: Environment & API Key Check](#step-1-environment--api-key-check)
3. [Step 2: Run the Model & Skill Test](#step-2-run-the-model--skill-test)
4. [Step 3: Test Audio Synthesis (edge-tts)](#step-3-test-audio-synthesis-edge-tts)
5. [Step 4: Launch the Streamlit Web Application](#step-4-launch-the-streamlit-web-application)
6. [Step 5: Testing Video Generation in the Browser](#step-5-testing-video-generation-in-the-browser)
7. [Troubleshooting & Common Questions](#troubleshooting--common-questions)
8. [The 3-Minute Hackathon Demo Rehearsal](#the-3-minute-hackathon-demo-rehearsal)

---

## 1. Prerequisites & Verification

Open **PowerShell** or your terminal inside the `stemations` folder:

```powershell
# 1. Verify Python version (Python 3.10+ required)
python --version

# 2. Verify all installed packages
pip list | findstr "google-genai streamlit edge-tts"
```

If any dependency is missing, install it with:
```powershell
pip install -r requirements.txt
```

---

## Step 1: Environment & API Key Check

Make sure your `.env` file exists in the root of the project with your Gemini API Key:

```ini
GEMINI_API_KEY=your_actual_key_here
```

*(Note: Your `.env` file is already protected by `.gitignore` and will never be committed to GitHub).*

---

## Step 2: Run the Model & Skill Test

Run the pre-configured verification script:

```powershell
python test_gemma.py
```

### Expected Output:
```text
[KEY] GEMINI_API_KEY detected. Connecting to Google GenAI...
[OK] Loaded Agent Skill: stem-animator (v1.0.0)
[INFO] Sending test request to model: gemma-4-26b-a4b-it...
[SUCCESS] Response received from gemma-4-26b-a4b-it:
--------------------------------------------------
An API, or Application Programming Interface, acts as a messenger...
--------------------------------------------------
[OK] System connection test passed! You are ready to run Stemations.
```

✅ **What this verifies:**
1. The **Agent Skill** (`skills/stem-animator/SKILL.md`) is successfully discovered and loaded.
2. The `google-genai` client connects to Google's open-weight **Gemma 4** model (`gemma-4-26b-a4b-it`).

---

## Step 3: Test Audio Synthesis (edge-tts)

Test the neural voice generation tool directly from the command line:

```powershell
python -c "from harness.tools.audio_tool import generate_voiceover; res = generate_voiceover('Testing Stemations neural voiceover synthesis.'); print('Voiceover Success:', res['success'], res['audio_path'])"
```

### Expected Output:
```text
Voiceover Success: True C:\Users\LENOVO\Documents\NTU\7th Sem\Hacktober\stemations\_output\audio\voice_*.mp3
```

You can open the generated `.mp3` file inside `_output/audio/` to hear the narration.

---

## Step 4: Launch the Streamlit Web Application

Start the interactive dashboard:

```powershell
streamlit run app.py
```

Streamlit will launch and display:
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Your default browser should open automatically. If not, navigate to `http://localhost:8501`.

---

## Step 5: Testing Video Generation in the Browser

Follow this sequence to test the complete agent loop:

1. **Pick a Topic:**
   - Click one of the quick starter buttons:
     - 🔍 **Binary Search**
     - 📐 **Pythagorean Theorem**
     - 🫧 **Bubble Sort**
     - ⚡ **Capacitor Charging**
   - *Or* type any topic (e.g., *"Newton's Second Law"*, *"Linked List Insertion"*).

2. **Select Model (in the Sidebar):**
   - Default is set to **`gemma-4-26b-a4b-it`** (Target model for the Gemma prize).
   - Alternatives available: `gemma-4-31b-it`, `gemini-3.8-flash`.

3. **Click "🚀 Run Stemations Agent":**
   - Watch the **Live Agent Execution Trace** in the right column:
     1. 📂 `[SKILL_LOAD]`: Loads vertical 9:16 layout rules from `SKILL.md`.
     2. 🧠 `[GEMMA_REASONING]`: Synthesizes the script, Manim code, and follow-up topics.
     3. 🎬 `[TOOL_MANIM]`: Runs the sandboxed code compiler (with self-healing if a syntax error occurs).
     4. 🎙️ `[TOOL_TTS]`: Synthesizes neural voiceover using `edge-tts`.
     5. 🎞️ `[TOOL_COMPOSE]`: Synchronizes video and audio into a vertical 9:16 MP4.

4. **Review the Generated Output:**
   - **Video Preview:** Play the 9:16 animated video.
   - **Download Button:** Click to download `stemation_<topic>.mp4`.
   - **Narration Script & Audio:** Listen to the standalone audio player.
   - **Synthesized Code:** Expand the code viewer to inspect the generated Manim Python script.
   - **Curriculum Pathway:** View 3 recommended next topics suggested by Gemma 4.

---

## 🛠️ Troubleshooting & Common Questions

| Issue | Cause | Fix |
|---|---|---|
| `GEMINI_API_KEY is not set` | Missing `.env` | Ensure `.env` exists in the `stemations` folder and contains `GEMINI_API_KEY="..."` |
| `manim: command not found` | Manim / FFmpeg not installed | Install FFmpeg via `winget install Gyan.FFmpeg` and `pip install manim` |
| `latex: command not found` | LaTeX missing on Windows | The `stem-animator` skill explicitly instructs Gemma to use unicode `Text()` to avoid requiring LaTeX! |
| Port 8501 busy | Previous Streamlit instance running | Run on another port: `streamlit run app.py --server.port 8502` |

---

## 🎤 The 3-Minute Hackathon Demo Rehearsal

Practice this timing with your team before presenting to the judges:

| Time | Phase | What to Say / Do |
|---|---|---|
| **0:00 - 0:20** (20s) | **The Problem** | *"Generative AI video models hallucinate math formulas and produce blurry, inaccurate pixels. Meanwhile, coding Manim animations by hand takes hours. We built Stemations to generate accurate 30-second explainers in seconds."* |
| **0:20 - 1:50** (90s) | **Live Demo** | Click **"Binary Search"** $\rightarrow$ Click **"Run Stemations Agent"** $\rightarrow$ Highlight the live **Agent Execution Trace** as it loads the skill and calls tools $\rightarrow$ Play the resulting 9:16 vertical animation with synchronized narration. |
| **1:50 - 2:20** (30s) | **Gemma & Skill** | *"We built an Agent Skill following the Open Standard (`SKILL.md`) that teaches Gemma 4 the 9:16 canvas rules and color schemes. Gemma acts as the scriptwriter, code generator, and self-healing compiler critic."* |
| **2:20 - 2:40** (20s) | **Curriculum Pathways** | Show the 3 recommended next topics at the bottom: *"Students are guided along an adaptive learning pathway to continue exploring deeper concepts."* |
| **2:40 - 3:00** (20s) | **Wrap-up** | Conclude and invite questions from the judges. |
