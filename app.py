"""
Stemations - Streamlit Interactive Dashboard & Agent Visualizer
Hacktoberfest Hack Day Faisalabad | Best Open-Source AI Project & Best Use of Gemma 4
"""
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Stemations - AI STEM Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for sleek modern dark theme
st.markdown("""
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
    .badge-bar {
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
    .pathway-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.shields.io/badge/Model-Gemma%204%20(Apache%202.0)-blue.svg", use_container_width=True)
    st.image("https://img.shields.io/badge/Standard-Agent%20Skill-green.svg", use_container_width=True)
    st.image("https://img.shields.io/badge/License-MIT-yellow.svg", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    model_choice = st.selectbox(
        "Gemma Model:",
        ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"],
        index=0,
        help="Calls Gemma 4 through the Google GenAI SDK (Gemini API)"
    )
    
    api_key_status = "✅ Set in .env" if os.getenv("GEMINI_API_KEY") else "⚠️ Missing in .env"
    st.markdown(f"**API Key Status:** `{api_key_status}`")
    
    st.markdown("---")
    st.markdown("### 🏆 Challenges")
    st.markdown("• **Best Open-Source AI Project**\n• **Best Use of Gemma 4**")
    st.markdown("---")
    st.markdown("### 👥 NTU Project Team (27-FYP-217)")
    st.caption("Maha Ather | Amina Asif | Haider Ali\nSupervisor: Sir Shahid")

# Header Section
st.markdown('<div class="main-header">🎬 Stemations</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Turn any STEM concept into an accurate, code-rendered 30-second animated explainer video using <b>Gemma 4</b> and the <b>Agent Skill Open Standard</b>.</div>',
    unsafe_allow_html=True
)

# Quick topic suggestions
col_sample1, col_sample2, col_sample3, col_sample4 = st.columns(4)
sample_topic = None

if col_sample1.button("🔍 Binary Search", use_container_width=True):
    sample_topic = "Binary Search in an Array"
if col_sample2.button("📐 Pythagorean Theorem", use_container_width=True):
    sample_topic = "Pythagorean Theorem Geometric Proof"
if col_sample3.button("🫧 Bubble Sort", use_container_width=True):
    sample_topic = "Bubble Sort Step-by-Step"
if col_sample4.button("⚡ Capacitor Charging", use_container_width=True):
    sample_topic = "Capacitor Charging RC Circuit"

# Input Form
with st.form("generation_form"):
    topic_input = st.text_input(
        "Enter any STEM or Technical Concept:",
        value=sample_topic if sample_topic else "Binary Search in an Array",
        placeholder="e.g. QuickSort, Newton's Second Law, Matrix Multiplication"
    )
    submit_button = st.form_submit_button("🚀 Run Stemations Agent", use_container_width=True, type="primary")

# Main execution logic
if submit_button and topic_input:
    col_video, col_details = st.columns([1, 1])
    
    with col_details:
        st.markdown("### 🧠 Live Agent Execution Trace")
        trace_container = st.container()
        
    with col_video:
        st.markdown("### 📱 9:16 Vertical Video Output")
        video_placeholder = st.empty()
        
    # Lazy import to avoid loading heavy modules before start
    try:
        from harness.agent import StemationsAgent
        
        # Real-time log hook for UI
        logs = []
        def ui_logger(phase, message):
            logs.append(f"**[{phase}]** {message}")
            with trace_container:
                st.markdown(f'<div class="step-box"><b>[{phase}]</b> {message}</div>', unsafe_allow_html=True)
                
        agent = StemationsAgent(model_name=model_choice, log_callback=ui_logger)
        
        with st.spinner("Stemations Agent is orchestrating Gemma 4 and Manim tools..."):
            result = agent.run(topic_input)
            
        if result["success"]:
            with col_video:
                if result.get("video_path") and Path(result["video_path"]).exists():
                    video_placeholder.video(result["video_path"])
                    
                    with open(result["video_path"], "rb") as file:
                        st.download_button(
                            label="⬇️ Download 9:16 Video (MP4)",
                            data=file,
                            file_name=f"stemation_{topic_input.replace(' ', '_').lower()}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                else:
                    video_placeholder.info("Scene rendered. Video file ready.")

            with col_details:
                st.success("🎉 Video generation completed successfully!")
                
                # Narration Script
                with st.expander("🎙️ Pedagogical Narration Script", expanded=True):
                    st.write(result.get("script", "No script available."))
                    if result.get("audio_path") and Path(result["audio_path"]).exists():
                        st.audio(result["audio_path"])
                        
                # Generated Code
                with st.expander("💻 Gemma 4 Synthesized Manim Code", expanded=False):
                    st.code(result.get("manim_code", "# No code available"), language="python")
                    
                # Learning Pathways
                next_topics = result.get("next_topics", [])
                if next_topics:
                    st.markdown("### 🗺️ Next Recommended Topics (Curriculum Pathway)")
                    st.caption("Students can continue their visual learning pathway by exploring:")
                    cols = st.columns(len(next_topics))
                    for idx, n_top in enumerate(next_topics):
                        cols[idx].info(f"**{idx+1}. {n_top}**")

        else:
            with col_details:
                st.error(f"Generation failed: {result.get('error')}")
                if "plan" in result:
                    with st.expander("Review Draft Code"):
                        st.code(result["plan"].get("manim_code", ""), language="python")

    except Exception as e:
        st.error(f"Execution halted: {e}")
        st.info("Check your .env file or run `test_gemma.py` to diagnose API connectivity.")
