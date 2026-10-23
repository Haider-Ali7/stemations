"""
Build pre-rendered demo bundles under demo_cache/ (full Manim + TTS + compose).
Run before the hackathon slot if Wi‑Fi is uncertain: python scripts/seed_demo_cache.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from harness.context import SkillContextLoader
from harness.plan_builder import StemationPlanBuilder
from harness.tools.audio_tool import generate_voiceover
from harness.tools.compose_tool import compose_video_and_audio
from harness.tools.manim_tool import render_manim_code

CACHE = ROOT / "demo_cache"

DEMOS = [
    {
        "id": "binary_search",
        "topic": "Binary Search in an Array",
        "keywords": ["binary", "search", "array"],
        "video_file": "binary_search.mp4",
        "script_file": "binary_search_script.txt",
        "code_file": "binary_search_scene.py",
    },
    {
        "id": "pythagoras",
        "topic": "Pythagorean Theorem Geometric Proof",
        "keywords": ["pythag", "theorem", "geometry"],
        "video_file": "pythagoras.mp4",
        "script_file": "pythagoras_script.txt",
        "code_file": "pythagoras_scene.py",
    },
]


class _OfflineLLM:
    def generate_stemation(self, topic: str):
        raise RuntimeError("offline seed")


def build_one(demo: dict) -> None:
    topic = demo["topic"]
    print(f"\n=== Building demo: {topic} ===")

    builder = StemationPlanBuilder(_OfflineLLM(), SkillContextLoader())
    plan, _source, _ = builder.build(topic)

    code = plan["manim_code"]
    script = plan["narration_script"]

    render = render_manim_code(code, output_dir=str(CACHE / "_build" / demo["id"]))
    if not render["success"]:
        raise RuntimeError(f"Manim failed for {demo['id']}: {render['error']}")

    audio = generate_voiceover(script, output_dir=str(CACHE / "_build" / demo["id"] / "audio"))
    if not audio["success"]:
        raise RuntimeError(f"TTS failed: {audio['error']}")

    compose = compose_video_and_audio(
        render["video_path"],
        audio["audio_path"],
        output_dir=str(CACHE / "_build" / demo["id"] / "final"),
    )
    if not compose["success"]:
        raise RuntimeError(f"Compose failed: {compose['error']}")

    dest_video = CACHE / demo["video_file"]
    shutil.copy2(compose["final_video_path"], dest_video)
    (CACHE / demo["script_file"]).write_text(script, encoding="utf-8")
    (CACHE / demo["code_file"]).write_text(code, encoding="utf-8")
    print(f"Saved {dest_video}")


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    for demo in DEMOS:
        build_one(demo)

    manifest = {
        "demos": [
            {
                "id": d["id"],
                "title": d["topic"],
                "keywords": d["keywords"],
                "video_file": d["video_file"],
                "script_file": d["script_file"],
                "code_file": d["code_file"],
                "next_topics": [],
            }
            for d in DEMOS
        ]
    }
    (CACHE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("\nDone. demo_cache/manifest.json updated.")


if __name__ == "__main__":
    main()
