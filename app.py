"""
Stemations - Streamlit Interactive Dashboard & Agent Visualizer
Hacktoberfest Hack Day Faisalabad | Best Open-Source AI Project & Best Use of Gemma 4
"""
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from harness.models import AVAILABLE_MODELS, DEFAULT_MODEL
from harness.demo_cache import find_demo_for_topic, get_demo_by_id, list_ready_demos
from harness.health import run_health_check

st.set_page_config(
    page_title="Stemations — Autonomous STEM Video Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "topic" not in st.session_state:
    st.session_state.topic = "Binary Search in an Array"

# ---------------------------------------------------------
# Modern, High-End Design System (Dark Glassmorphic Theme)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 1) 100%);
        color: #F8FAFC;
    }

    /* Hero Header Container */
    .hero-card {
        text-align: center;
        padding: 2.2rem 1.5rem 1.8rem 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 16px;
        border-radius: 9999px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38BDF8;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.9rem;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 3.0rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.6rem;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.15rem;
        max-width: 720px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Terminal Trace Box */
    .terminal-container {
        background: #090D16;
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.6);
        max-height: 480px;
        overflow-y: auto;
    }

    .terminal-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 0.7rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #64748B;
    }

    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-red { background: #EF4444; }
    .dot-yellow { background: #F59E0B; }
    .dot-green { background: #10B981; }

    .step-box {
        background: rgba(30, 41, 59, 0.55);
        border-left: 3px solid #38BDF8;
        padding: 0.6rem 0.9rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
        color: #E2E8F0;
        display: flex;
        align-items: baseline;
        gap: 10px;
        transition: all 0.2s ease;
    }
    .step-box:hover {
        background: rgba(30, 41, 59, 0.9);
        border-left-color: #818CF8;
    }

    .step-tag {
        font-weight: 700;
        font-size: 0.74rem;
        padding: 2px 6px;
        border-radius: 4px;
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        letter-spacing: 0.5px;
    }

    /* Smartphone Device Frame for 9:16 Video Preview */
    .device-showcase {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(180deg, #0F172A 0%, #090D16 100%);
        border: 2px solid #334155;
        border-radius: 24px;
        padding: 16px 16px 18px 16px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.05);
        margin: 0 auto 1.2rem auto;
        max-width: 330px;
    }

    .device-notch {
        width: 70px;
        height: 6px;
        background: #334155;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    /* Responsive Streamlit Video */
    div[data-testid="stVideo"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    div[data-testid="stVideo"] video {
        max-height: 480px !important;
        width: auto !important;
        aspect-ratio: 9 / 16 !important;
        border-radius: 16px !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    /* Topic card */
    .pathway-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #F8FAFC;
        font-weight: 600;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pathway-card:hover {
        transform: translateX(4px);
        border-color: #38BDF8;
        background: rgba(30, 41, 59, 0.8);
    }

    .pathway-badge {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* Form styling */
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Configuration & Fail-Safe Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎬 **Stemations**")
    st.caption("Autonomous STEM Animation Agent")

    st.markdown("---")
    st.markdown("### ⚙️ **Model & Engine**")

    default_index = AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0
    model_choice = st.selectbox(
        "Active Model:",
        AVAILABLE_MODELS,
        index=default_index,
        help="Gemini 3.5 Flash is ultra-fast & reliable. Gemma 4 is available for open-weight compliance.",
    )

    api_ok = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    st.markdown(
        f"**API Status:** {'🟢 Connected (.env)' if api_ok else '🔴 Missing GEMINI_API_KEY'}"
    )

    if st.button("🔍 Run System Diagnostic", use_container_width=True):
        with st.spinner("Verifying Manim, edge-tts, MoviePy, & API..."):
            report = run_health_check(test_api=api_ok)
        for line in report.messages:
            st.code(line, language=None)
        if report.ok:
            st.success("✅ System 100% Ready.")
        else:
            st.warning("⚠️ Review diagnostic issues above.")

    st.markdown("---")
    st.markdown("### 📼 **Venue Offline Demos**")
    ready_demos = list_ready_demos()
    if ready_demos:
        st.caption("Pre-rendered fail-safe cache (zero Wi-Fi required).")
        backup_id = st.selectbox(
            "Select cached demo:",
            options=[d["id"] for d in ready_demos],
            format_func=lambda i: next(d["title"] for d in ready_demos if d["id"] == i),
        )
        if st.button("▶ Play Offline Backup", use_container_width=True):
            st.session_state.play_backup_id = backup_id
    else:
        st.caption("No cache found. Run `python scripts/seed_demo_cache.py`")

    st.markdown("---")
    st.markdown("### 🏆 **Target Prize Categories**")
    st.markdown(
        """
        - 🥇 **Best Open-Source AI Project**
        - 🧠 **Best Use of Gemma 4**
        """
    )

    st.markdown("---")
    st.caption("NTU 27-FYP-217 | Maha Ather, Amina Asif, Haider Ali")
    st.caption("Open Source under MIT License")

# ---------------------------------------------------------
# Hero Header
# ---------------------------------------------------------
st.markdown(
    """
<div class="hero-card">
    <div class="badge-pill">✨ Powered by Google Gemma 4 & Agent Skill Open Standard</div>
    <div class="hero-title">Stemations</div>
    <div class="hero-subtitle">
        Transform any complex STEM concept into a mathematically precise, 9:16 vertical animated short 
        with synchronized neural narration and personalized learning pathways.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Quick Concept Starter Chips
# ---------------------------------------------------------
st.markdown("##### ⚡ **Quick Starters:**")
c1, c2, c3, c4 = st.columns(4)
if c1.button("🔍 Binary Search", use_container_width=True):
    st.session_state.topic = "Binary Search in an Array"
if c2.button("📐 Pythagorean Theorem", use_container_width=True):
    st.session_state.topic = "Pythagorean Theorem Geometric Proof"
if c3.button("🫧 Bubble Sort", use_container_width=True):
    st.session_state.topic = "Bubble Sort Step-by-Step"
if c4.button("⚡ Capacitor Charging", use_container_width=True):
    st.session_state.topic = "Capacitor Charging RC Circuit"

# ---------------------------------------------------------
# Main Generation Form
# ---------------------------------------------------------
with st.form("generation_form", clear_on_submit=False):
    col_input, col_btn = st.columns([4, 1.2])
    with col_input:
        topic_input = st.text_input(
            "Enter any STEM topic to animate:",
            value=st.session_state.topic,
            placeholder="e.g. Selection Sort, Newton's Second Law, QuickSort, Doppler Effect...",
            label_visibility="collapsed",
        )
    with col_btn:
        submit_button = st.form_submit_button(
            "🚀 Generate Stemation",
            use_container_width=True,
            type="primary",
        )

# ---------------------------------------------------------
# Offline Fail-Safe Demo Display (if triggered)
# ---------------------------------------------------------
if getattr(st.session_state, "play_backup_id", None):
    demo = get_demo_by_id(st.session_state.play_backup_id)
    if demo and demo.get("video_path"):
        st.info(f"📼 Streaming Pre-Rendered Venue Demo: **{demo.get('title', demo['id'])}**")
        col_vid, col_meta = st.columns([1, 1])
        with col_vid:
            st.video(demo["video_path"])
        with col_meta:
            st.markdown("### 🎙️ Pre-Rendered Script")
            st.write(demo.get("script", ""))
            with st.expander("💻 View Manim Code"):
                st.code(demo.get("manim_code", ""), language="python")

# ---------------------------------------------------------
# Live Agent Generation Loop
# ---------------------------------------------------------
if submit_button and topic_input:
    st.session_state.topic = topic_input

    if not api_ok:
        st.error("⚠️ GEMINI_API_KEY is missing in your `.env` file. Add your key from Google AI Studio.")
        cached = find_demo_for_topic(topic_input)
        if cached and cached.get("video_path"):
            st.warning("Playing matching offline backup demo instead.")
            st.video(cached["video_path"])
        st.stop()

    st.markdown("---")
    col_video, col_details = st.columns([1, 1.2])

    with col_video:
        st.markdown("### 📱 **9:16 Video Player**")
        st.caption("Fitted for desktop viewing • Downloads in full 1080×1920 mobile format")
        video_placeholder = st.empty()

    with col_details:
        st.markdown("### 🧠 **Agent Intelligence Deck**")
        trace_placeholder = st.empty()

    try:
        from harness.agent import StemationsAgent

        trace_events = []

        def ui_logger(phase: str, message: str):
            trace_events.append({"phase": phase, "message": message})
            with trace_placeholder.container():
                st.markdown(
                    """
                    <div class="terminal-container">
                        <div class="terminal-bar">
                            <span class="dot dot-red"></span>
                            <span class="dot dot-yellow"></span>
                            <span class="dot dot-green"></span>
                            <span style="margin-left: 8px;">stemations-agent --live-trace</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                for ev in trace_events:
                    st.markdown(
                        f"""
                        <div class="step-box">
                            <span class="step-tag">[{ev['phase']}]</span>
                            <span>{ev['message']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        agent = StemationsAgent(model_name=model_choice, log_callback=ui_logger)

        with st.spinner("🧠 Agent reasoning: Planning 4-beat lesson → Rendering Manim → Synthesizing voice..."):
            result = agent.run(topic_input)

        if result["success"]:
            # Display Video
            with col_video:
                if result.get("video_path") and Path(result["video_path"]).exists():
                    video_placeholder.video(result["video_path"])
                    with open(result["video_path"], "rb") as file:
                        st.download_button(
                            label="⬇️ Download 1080×1920 Mobile MP4",
                            data=file,
                            file_name=f"stemation_{topic_input.replace(' ', '_').lower()}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                            type="secondary",
                        )
                else:
                    video_placeholder.warning("⚠️ Video rendered but output path was not found.")

            # Display Inspector Deck
            with col_details:
                st.success("🎉 Video generation & composition complete!")
                
                meta_info = []
                if result.get("model_used"):
                    meta_info.append(f"Model: `{result['model_used']}`")
                if result.get("plan_source"):
                    meta_info.append(f"Source: `{result['plan_source']}`")
                if meta_info:
                    st.caption(" · ".join(meta_info))

                tab_script, tab_code, tab_curriculum = st.tabs(
                    ["🎙️ Voiceover Script", "💻 Manim CE Code", "🗺️ Next Topics Pathway"]
                )

                with tab_script:
                    st.markdown("##### Spoken Narration Script")
                    st.write(result.get("script", ""))
                    if result.get("audio_path") and Path(result["audio_path"]).exists():
                        st.markdown("##### Standalone Audio Track")
                        st.audio(result["audio_path"])

                with tab_code:
                    st.markdown("##### Sandboxed Manim Scene Code")
                    st.code(result.get("manim_code", ""), language="python")

                with tab_curriculum:
                    st.markdown("##### Recommended Follow-Up Curriculum")
                    next_topics = result.get("next_topics", [])
                    if next_topics:
                        for idx, n_top in enumerate(next_topics):
                            st.markdown(
                                f"""
                                <div class="pathway-card">
                                    <div class="pathway-badge">{idx + 1}</div>
                                    <div>{n_top}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No follow-up topics generated.")

        else:
            with col_details:
                st.error(f"Generation failed: {result.get('error')}")
                cached = find_demo_for_topic(topic_input)
                if cached and cached.get("video_path"):
                    st.warning("Loaded matching fail-safe demo from cache.")
                    with col_video:
                        video_placeholder.video(cached["video_path"])
                if "plan" in result:
                    with st.expander("Draft Code"):
                        st.code(result["plan"].get("manim_code", ""), language="python")

    except Exception as e:
        st.error(f"Execution halted: {e}")
        st.info("Run `python verify_setup.py` to diagnose your environment.")
