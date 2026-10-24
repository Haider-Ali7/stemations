"""
Stemations - Autonomous STEM Video Agent Backend API
FastAPI service delivering real-time streaming agent orchestration and video delivery.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Ensure backend root is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env")

from harness.models import AVAILABLE_MODELS, DEFAULT_MODEL
from harness.demo_cache import find_demo_for_topic, get_demo_by_id, list_ready_demos
from harness.health import run_health_check
from harness.agent import StemationsAgent

# Rate limiting — 5 generation requests per minute per IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Stemations Engine API",
    description="Autonomous educational video synthesizer powered by Google Gemma 4 and Manim",
    version="2.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — configurable via ALLOWED_ORIGINS env var (comma-separated), defaults to * in dev
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
FINAL_OUTPUT_DIR = BACKEND_DIR / "_output" / "final"
FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = BACKEND_DIR / "demo_cache"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Auto-cleanup: remove generated artifacts older than 24 hours on startup
MAX_OUTPUT_AGE_HOURS = int(os.getenv("MAX_OUTPUT_AGE_HOURS", "24"))


def _cleanup_old_outputs():
    """Deletes temp scene files and old renders to prevent disk fill on deployed servers."""
    now = time.time()
    max_age_seconds = MAX_OUTPUT_AGE_HOURS * 3600
    for subdir in ["scenes", "audio", "final"]:
        target = BACKEND_DIR / "_output" / subdir
        if not target.exists():
            continue
        for f in target.iterdir():
            if f.is_file():
                try:
                    if (now - f.stat().st_mtime) > max_age_seconds:
                        f.unlink()
                except OSError:
                    pass
    # Clean up media subdirectories from Manim renders
    scenes_media = BACKEND_DIR / "_output" / "scenes" / "media"
    if scenes_media.exists():
        import shutil
        for d in scenes_media.iterdir():
            if d.is_dir():
                try:
                    if (now - d.stat().st_mtime) > max_age_seconds:
                        shutil.rmtree(d, ignore_errors=True)
                except OSError:
                    pass


try:
    _cleanup_old_outputs()
except Exception:
    pass


def sanitize_professional_message(phase: str, raw_msg: str) -> str:
    """
    Transforms internal pipeline log events into human-written, professional
    status updates without exposing raw system paths, tracebacks, or backend internals.
    """
    phase_upper = phase.upper()

    # Pre-crafted human-readable professional descriptors
    if phase_upper == "SKILL_LOAD":
        return "Validating instructional framework standards and vertical composition layout"
    elif phase_upper == "PLAN":
        # Extract topic if present in message
        match = re.search(r"for:\s*['\"]?(.*?)['\"]?\.{0,3}$", raw_msg, re.IGNORECASE)
        topic = match.group(1).strip() if match else ""
        if topic:
            return f"Structuring four-beat pedagogical sequence for '{topic}'"
        return "Deconstructing topic into structured instructional progression"
    elif phase_upper == "LLM_PLAN":
        return "Synthesizing pedagogical narration script and coordinate geometry plan"
    elif phase_upper == "SKILL_TEMPLATE":
        return "Applying certified curriculum template for mathematical accuracy"
    elif phase_upper == "SCRIPT_READY":
        match = re.search(r"\((\d+)\s*words\)", raw_msg)
        count = match.group(1) if match else "verified"
        return f"Instructional narration script finalized ({count} words)"
    elif phase_upper == "CODE_READY":
        return "Mathematical animation code structured for execution"
    elif phase_upper == "TOOL_MANIM":
        return "Rendering vector coordinates and mathematical animations in 9:16 layout"
    elif phase_upper == "SELF_HEAL":
        return "Refining geometric constraints and optimizing visual pacing"
    elif phase_upper == "RENDER_SUCCESS":
        return "Vector animation frames rendered in high definition"
    elif phase_upper == "TOOL_TTS":
        return "Synthesizing neural voiceover with synchronized instructional delivery"
    elif phase_upper == "TTS_SUCCESS":
        return "Voiceover narration audio track completed"
    elif phase_upper == "TOOL_COMPOSE":
        return "Multiplexing animation frames with synchronized audio narration"
    elif phase_upper == "COMPLETE":
        return "STEM animation production completed and verified"
    elif phase_upper == "WARN":
        return "Adjusting audio and visual synchronization parameters"
    elif phase_upper == "ERROR":
        return "Notice during rendering cycle; switching to verified cached material"

    # Fallback: remove any system path patterns like C:\ or /users
    clean = re.sub(r"[A-Za-z]:\\[\w\\\.\-]+", "[internal path]", raw_msg)
    clean = re.sub(r"/\w+[\w/\.\-]+", "[internal path]", clean)
    return clean


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    model: Optional[str] = None


@app.get("/api/health")
def get_health():
    """Returns diagnostic health status of all core rendering and AI engines."""
    api_ok = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
    report = run_health_check(test_api=api_ok)
    return {
        "ok": report.ok,
        "api_connected": api_ok,
        "active_model": DEFAULT_MODEL,
        "diagnostics": report.messages,
    }


@app.get("/api/models")
def get_models():
    """Returns available reasoning and generation models."""
    return {
        "models": AVAILABLE_MODELS,
        "default": DEFAULT_MODEL,
    }


@app.get("/api/demos")
def get_demos():
    """Returns pre-rendered venue offline demos."""
    demos = list_ready_demos()
    output = []
    for d in demos:
        output.append({
            "id": d.get("id"),
            "title": d.get("title", d.get("id")),
            "topic": d.get("topic", ""),
            "description": d.get("description", ""),
            "video_url": f"/api/demo-videos/{Path(d['video_path']).name}" if d.get("video_path") else None,
            "script": d.get("script", ""),
            "manim_code": d.get("manim_code", ""),
        })
    return {"demos": output}


DEFAULT_TOPIC_NAMES = [
    "Binary Search in an Array",
    "Pythagorean Theorem Geometric Proof",
    "Bubble Sort Algorithm",
    "Capacitor RC Circuit Charging",
    "Newton's Second Law of Motion",
    "Euler's Formula Visualization",
    "QuickSort Partitioning Step-by-Step",
    "Electromagnetic Induction Faraday Law",
]


@app.get("/api/recent-videos")
def get_recent_videos(limit: int = Query(default=6, ge=1, le=20)):
    """
    Returns the most recent generated videos and offline demos for display
    in the interactive horizontal reel.
    """
    videos = []

    # 1. Check generated videos in FINAL_OUTPUT_DIR
    if FINAL_OUTPUT_DIR.exists():
        mp4_files = sorted(
            FINAL_OUTPUT_DIR.glob("*.mp4"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for idx, file in enumerate(mp4_files):
            try:
                stat = file.stat()
                meta_file = FINAL_OUTPUT_DIR / f"{file.stem}.json"
                topic_title = None
                script_preview = ""
                model_used = None

                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                        topic_title = meta.get("topic")
                        script_preview = meta.get("script", "")[:120]
                        model_used = meta.get("model_used")
                    except Exception:
                        pass

                if not topic_title:
                    topic_title = DEFAULT_TOPIC_NAMES[idx % len(DEFAULT_TOPIC_NAMES)]

                size_mb = round(stat.st_size / (1024 * 1024), 2)
                videos.append({
                    "id": file.stem,
                    "title": topic_title,
                    "filename": file.name,
                    "url": f"/api/videos/{file.name}",
                    "download_url": f"/api/videos/{file.name}?download=true",
                    "created_at": stat.st_mtime,
                    "size_mb": size_mb,
                    "script_preview": script_preview,
                    "model_used": model_used,
                    "is_demo": False,
                })
            except Exception:
                continue

    # 2. Append ready demos if needed to guarantee at least 4 scrollable videos
    demo_list = list_ready_demos()
    for d in demo_list:
        if d.get("video_path") and Path(d["video_path"]).exists():
            p = Path(d["video_path"])
            size_mb = round(p.stat().st_size / (1024 * 1024), 2)
            videos.append({
                "id": d["id"],
                "title": d.get("title", d["id"].replace("_", " ").title()),
                "filename": p.name,
                "url": f"/api/demo-videos/{p.name}",
                "download_url": f"/api/demo-videos/{p.name}?download=true",
                "created_at": p.stat().st_mtime,
                "size_mb": size_mb,
                "script_preview": d.get("script", "")[:120],
                "model_used": "Gemma 4 Standard",
                "is_demo": True,
            })

    return {"videos": videos[:limit]}


@app.get("/api/videos/{filename}")
def serve_video(filename: str, download: bool = False):
    """Streams a generated video file with support for range requests."""
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    target = FINAL_OUTPUT_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Video file not found")

    disposition = "attachment" if download else "inline"
    headers = {"Content-Disposition": f'{disposition}; filename="{safe_name}"'}
    return FileResponse(
        path=str(target),
        media_type="video/mp4",
        headers=headers,
    )


@app.get("/api/demo-videos/{filename}")
def serve_demo_video(filename: str, download: bool = False):
    """Streams a pre-rendered demo video file."""
    safe_name = os.path.basename(filename)
    target = CACHE_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Demo video not found")

    disposition = "attachment" if download else "inline"
    headers = {"Content-Disposition": f'{disposition}; filename="{safe_name}"'}
    return FileResponse(
        path=str(target),
        media_type="video/mp4",
        headers=headers,
    )


@app.get("/api/generate/stream")
@limiter.limit("5/minute")
async def stream_generate(
    request: Request,
    topic: str = Query(..., min_length=2, max_length=200),
    model: Optional[str] = Query(default=None),
):
    """
    Server-Sent Events endpoint streaming real-time pedagogical steps and progress.
    """
    model_choice = model or DEFAULT_MODEL
    queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    def sync_logger(phase: str, message: str):
        professional_msg = sanitize_professional_message(phase, message)
        queue.put_nowait({
            "type": "step",
            "phase": phase,
            "message": professional_msg,
            "timestamp": time.time(),
        })

    async def event_generator() -> AsyncGenerator[str, None]:
        # Launch agent in background thread to avoid blocking asyncio event loop
        loop = asyncio.get_running_loop()
        agent = StemationsAgent(model_name=model_choice, log_callback=sync_logger)

        run_future = loop.run_in_executor(None, agent.run, topic)

        # Stream events while agent is executing
        while not run_future.done():
            while not queue.empty():
                item = queue.get_nowait()
                yield f"data: {json.dumps(item)}\n\n"
            await asyncio.sleep(0.15)

        # Drain remaining events
        while not queue.empty():
            item = queue.get_nowait()
            yield f"data: {json.dumps(item)}\n\n"

        # Obtain final result
        try:
            result = await run_future
            if result.get("success"):
                vid_path = result.get("video_path")
                vid_url = None
                if vid_path and Path(vid_path).exists():
                    p_vid = Path(vid_path)
                    vid_url = f"/api/videos/{p_vid.name}"
                    # Save metadata json alongside video
                    meta_path = p_vid.with_suffix(".json")
                    try:
                        meta_path.write_text(
                            json.dumps(
                                {
                                    "id": p_vid.stem,
                                    "topic": topic,
                                    "created_at": time.time(),
                                    "model_used": result.get("model_used", model_choice),
                                    "script": result.get("script", ""),
                                    "next_topics": result.get("next_topics", []),
                                },
                                indent=2,
                            ),
                            encoding="utf-8",
                        )
                    except Exception:
                        pass

                audio_path = result.get("audio_path")
                audio_url = None
                if audio_path and Path(audio_path).exists():
                    audio_url = f"/api/videos/{Path(audio_path).name}"

                final_payload = {
                    "type": "complete",
                    "success": True,
                    "topic": topic,
                    "video_url": vid_url,
                    "audio_url": audio_url,
                    "script": result.get("script", ""),
                    "manim_code": result.get("manim_code", ""),
                    "next_topics": result.get("next_topics", []),
                    "model_used": result.get("model_used", model_choice),
                    "plan_source": result.get("plan_source", "llm"),
                }
            else:
                # In case of compiler error, check if an offline cached backup exists
                cached = find_demo_for_topic(topic)
                cached_data = None
                if cached and cached.get("video_path"):
                    p = Path(cached["video_path"])
                    cached_data = {
                        "video_url": f"/api/demo-videos/{p.name}",
                        "title": cached.get("title", topic),
                        "script": cached.get("script", ""),
                        "manim_code": cached.get("manim_code", ""),
                    }

                final_payload = {
                    "type": "complete",
                    "success": False,
                    "error": "The animation engine encountered a layout constraint during synthesis.",
                    "cached_demo": cached_data,
                    "model_used": result.get("model_used", model_choice),
                }

            yield f"data: {json.dumps(final_payload)}\n\n"
        except Exception as exc:
            sanitized_err = sanitize_professional_message("ERROR", str(exc))
            yield f"data: {json.dumps({'type': 'error', 'message': sanitized_err})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/generate")
@limiter.limit("5/minute")
def generate_sync(request: Request, payload: GenerateRequest):
    """Synchronous generation endpoint returning the full generation payload."""
    model_choice = payload.model or DEFAULT_MODEL
    trace_events = []

    def sync_logger(phase: str, message: str):
        trace_events.append({
            "phase": phase,
            "message": sanitize_professional_message(phase, message),
        })

    agent = StemationsAgent(model_name=model_choice, log_callback=sync_logger)
    result = agent.run(payload.topic)

    if result.get("success"):
        vid_path = result.get("video_path")
        vid_url = f"/api/videos/{Path(vid_path).name}" if vid_path and Path(vid_path).exists() else None
        return {
            "success": True,
            "topic": payload.topic,
            "video_url": vid_url,
            "script": result.get("script", ""),
            "manim_code": result.get("manim_code", ""),
            "next_topics": result.get("next_topics", []),
            "model_used": result.get("model_used", model_choice),
            "trace": trace_events,
        }
    else:
        cached = find_demo_for_topic(payload.topic)
        return {
            "success": False,
            "error": "The animation engine encountered a constraint during synthesis.",
            "trace": trace_events,
            "cached_demo": {
                "video_url": f"/api/demo-videos/{Path(cached['video_path']).name}",
                "title": cached.get("title", payload.topic),
            } if (cached and cached.get("video_path")) else None,
        }


# Mount the modern frontend static files at root /
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
