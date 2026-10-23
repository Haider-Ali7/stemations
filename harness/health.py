"""
Environment and dependency checks before a live demo.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv


@dataclass
class HealthReport:
    ok: bool = True
    messages: List[str] = field(default_factory=list)

    def add(self, label: str, passed: bool, detail: str = "") -> None:
        icon = "OK" if passed else "FAIL"
        line = f"[{icon}] {label}"
        if detail:
            line += f" — {detail}"
        self.messages.append(line)
        if not passed:
            self.ok = False


def run_health_check(test_api: bool = True) -> HealthReport:
    load_dotenv()
    report = HealthReport()

    key = os.getenv("GEMINI_API_KEY", "")
    report.add(
        "GEMINI_API_KEY",
        bool(key and key != "your_gemini_api_key_here"),
        "Set in .env from https://aistudio.google.com/",
    )

    try:
        import streamlit  # noqa: F401
        report.add("streamlit", True)
    except ImportError:
        report.add("streamlit", False, "pip install -r requirements.txt")

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "manim", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        report.add("manim", proc.returncode == 0, (proc.stdout or proc.stderr).strip()[:80])
    except Exception as exc:
        report.add("manim", False, str(exc))

    try:
        import edge_tts  # noqa: F401
        report.add("edge-tts", True)
    except ImportError:
        report.add("edge-tts", False)

    moviepy_ok = False
    try:
        from moviepy import VideoFileClip  # noqa: F401
        moviepy_ok = True
    except ImportError:
        try:
            from moviepy.editor import VideoFileClip  # noqa: F401
            moviepy_ok = True
        except ImportError:
            pass
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    report.add("moviepy or ffmpeg", moviepy_ok or ffmpeg_ok)

    if test_api and key and key != "your_gemini_api_key_here":
        try:
            from google import genai
            from harness.models import DEFAULT_MODEL

            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents="Reply with exactly: OK",
            )
            report.add("Google GenAI", bool(response and response.text), DEFAULT_MODEL)
        except Exception as exc:
            report.add("Google GenAI", False, str(exc)[:120])

    return report
