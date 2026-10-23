"""
Pre-rendered demo bundles for venue Wi‑Fi / API outages (see demo_cache/README.md).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "demo_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"


def load_manifest() -> List[Dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        return []
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return data.get("demos", [])
    except (json.JSONDecodeError, OSError):
        return []


def find_demo_for_topic(topic: str) -> Optional[Dict[str, Any]]:
    topic_lower = topic.lower()
    best: Optional[Dict[str, Any]] = None
    best_score = 0
    for demo in load_manifest():
        score = 0
        for kw in demo.get("keywords", []):
            if kw.lower() in topic_lower:
                score += 1
        if score > best_score:
            best_score = score
            best = demo
    if best and best_score > 0:
        return _resolve_paths(best)
    return None


def get_demo_by_id(demo_id: str) -> Optional[Dict[str, Any]]:
    for demo in load_manifest():
        if demo.get("id") == demo_id:
            return _resolve_paths(demo)
    return None


def _resolve_paths(demo: Dict[str, Any]) -> Dict[str, Any]:
    resolved = dict(demo)
    video = CACHE_DIR / demo["video_file"]
    resolved["video_path"] = str(video) if video.exists() else None
    script_file = demo.get("script_file")
    if script_file:
        path = CACHE_DIR / script_file
        resolved["script"] = path.read_text(encoding="utf-8") if path.exists() else demo.get("script", "")
    code_file = demo.get("code_file")
    if code_file:
        path = CACHE_DIR / code_file
        resolved["manim_code"] = path.read_text(encoding="utf-8") if path.exists() else demo.get("manim_code", "")
    return resolved


def list_ready_demos() -> List[Dict[str, Any]]:
    ready = []
    for demo in load_manifest():
        resolved = _resolve_paths(demo)
        if resolved.get("video_path"):
            ready.append(resolved)
    return ready
