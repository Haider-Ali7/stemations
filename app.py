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
    page_title="Stemations - AI STEM Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "topic" not in st.session_state:
    st.session_state.topic = "Binary Search in an Array"

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .step-box {
        background-color: #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
        font-family: monospace;
        color: #E2E8F0;
    }
    /* Responsive Web Video Frame for Vertical 9:16 */
    div[data-testid="stVideo"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background: #0B1120;
        border-radius: 16px;
        padding: 10px;
        border: 1px solid #1E293B;
    }
    div[data-testid="stVideo"] video {
        max-height: 490px !important;
        width: auto !important;
        aspect-ratio: 9 / 16 !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.7) !important;
        border: 2px solid #334155 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image(
        "https://img.shields.io/badge/Model-Gemma%204%20(Apache%202.0)-blue.svg",
        use_container_width=True,
    )
    st.image(
        "https://img.shields.io/badge/Standard-Agent%20Skill-green.svg",
        use_container_width=True,
    )
    st.image("https://img.shields.io/badge/License-MIT-yellow.svg", use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    default_index = AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0
    model_choice = st.selectbox(
        "Model:",
        AVAILABLE_MODELS,
        index=default_index,
        help="Gemini 3.x recommended live. Gemma 4 listed for open-weight compliance; may 500 on some keys.",
    )

    api_ok = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    st.markdown(f"**API Key:** {'✅ .env' if api_ok else '⚠️ missing'}")

    if st.button("🔍 Run system check", use_container_width=True):
        with st.spinner("Checking Manim, TTS, API..."):
            report = run_health_check(test_api=api_ok)
        for line in report.messages:
            st.code(line, language=None)
        if report.ok:
            st.success("Ready for live generation.")
        else:
            st.warning("Fix FAIL items before judging slot.")

    ready_demos = list_ready_demos()
    st.markdown("---")
    st.markdown("### 📼 Venue backup demos")
    if ready_demos:
        st.caption("Pre-rendered (full Manim pipeline). Use if Wi‑Fi/API fails.")
        backup_id = st.selectbox(
            "Play cached demo",
            options=[d["id"] for d in ready_demos],
            format_func=lambda i: next(d["title"] for d in ready_demos if d["id"] == i),
        )
        if st.button("▶ Show backup video", use_container_width=True):
            st.session_state.play_backup_id = backup_id
    else:
        st.caption("No MP4 in demo_cache yet. Run: `python scripts/seed_demo_cache.py`")

    st.markdown("---")
    st.markdown("### 🏆 Challenges")
    st.markdown("• **Best Open-Source AI Project**\n• **Best Use of Gemma 4**")
    st.markdown("---")
    st.caption("NTU 27-FYP-217 | Maha Ather, Amina Asif, Haider Ali")

st.markdown('<div class="main-header">🎬 Stemations</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">STEM concept → Agent Skill + LLM plan → Manim 9:16 animation → neural voiceover → learning pathway.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
if c1.button("🔍 Binary Search", use_container_width=True):
    st.session_state.topic = "Binary Search in an Array"
if c2.button("📐 Pythagorean Theorem", use_container_width=True):
    st.session_state.topic = "Pythagorean Theorem Geometric Proof"
if c3.button("🫧 Bubble Sort", use_container_width=True):
    st.session_state.topic = "Bubble Sort Step-by-Step"
if c4.button("⚡ Capacitor Charging", use_container_width=True):
    st.session_state.topic = "Capacitor Charging RC Circuit"

with st.form("generation_form"):
    topic_input = st.text_input(
        "STEM concept:",
        value=st.session_state.topic,
        placeholder="e.g. QuickSort, Newton's Second Law",
    )
    submit_button = st.form_submit_button("🚀 Run Stemations Agent", use_container_width=True, type="primary")

if getattr(st.session_state, "play_backup_id", None):
    demo = get_demo_by_id(st.session_state.play_backup_id)
    if demo and demo.get("video_path"):
        st.info(f"Venue backup: **{demo.get('title', demo['id'])}** (pre-rendered)")
        st.video(demo["video_path"])
        with st.expander("Script & code from cache"):
            st.write(demo.get("script", ""))
            st.code(demo.get("manim_code", ""), language="python")

if submit_button and topic_input:
    st.session_state.topic = topic_input

    if not api_ok:
        st.error("GEMINI_API_KEY missing in .env — add your key from Google AI Studio.")
        cached = find_demo_for_topic(topic_input)
        if cached and cached.get("video_path"):
            st.warning("Showing matching backup demo instead.")
            st.video(cached["video_path"])
        st.stop()

    col_video, col_details = st.columns([1, 1])

    with col_details:
        st.markdown("### 🧠 Live Agent Trace")
        trace_container = st.container()

    with col_video:
        st.markdown("### 📱 9:16 Video Player")
        st.caption("Fitted for desktop viewing • Downloads in full 1080×1920 mobile format")
        video_placeholder = st.empty()

    try:
        from harness.agent import StemationsAgent

        def ui_logger(phase, message):
            with trace_container:
                st.markdown(
                    f'<div class="step-box"><b>[{phase}]</b> {message}</div>',
                    unsafe_allow_html=True,
                )

        agent = StemationsAgent(model_name=model_choice, log_callback=ui_logger)

        with st.spinner("Running pipeline: plan → Manim → TTS → compose..."):
            result = agent.run(topic_input)

        if result["success"]:
            meta = []
            if result.get("model_used"):
                meta.append(f"Model: `{result['model_used']}`")
            if result.get("plan_source"):
                meta.append(f"Plan: `{result['plan_source']}`")
            if meta:
                st.caption(" · ".join(meta))

            with col_video:
                if result.get("video_path") and Path(result["video_path"]).exists():
                    video_placeholder.video(result["video_path"])
                    with open(result["video_path"], "rb") as file:
                        st.download_button(
                            label="⬇️ Download MP4",
                            data=file,
                            file_name=f"stemation_{topic_input.replace(' ', '_').lower()}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )
                else:
                    video_placeholder.warning("Video path missing.")

            with col_details:
                st.success("Video generation completed.")
                with st.expander("🎙️ Narration script", expanded=True):
                    st.write(result.get("script", ""))
                    if result.get("audio_path") and Path(result["audio_path"]).exists():
                        st.audio(result["audio_path"])
                with st.expander("💻 Manim code", expanded=False):
                    st.code(result.get("manim_code", ""), language="python")
                next_topics = result.get("next_topics", [])
                if next_topics:
                    st.markdown("### 🗺️ Next topics")
                    for idx, n_top in enumerate(next_topics):
                        st.info(f"**{idx + 1}.** {n_top}")
        else:
            with col_details:
                st.error(f"Generation failed: {result.get('error')}")
                cached = find_demo_for_topic(topic_input)
                if cached and cached.get("video_path"):
                    st.warning("Loaded matching **demo_cache** backup (same skill templates / prior render).")
                    with col_video:
                        video_placeholder.video(cached["video_path"])
                if "plan" in result:
                    with st.expander("Draft Manim code"):
                        st.code(result["plan"].get("manim_code", ""), language="python")

    except Exception as e:
        st.error(f"Execution halted: {e}")
        st.info("Run `python verify_setup.py` to diagnose your environment.")
