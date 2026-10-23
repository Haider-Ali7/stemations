"""
Stemation generation pipeline: plan → Manim → TTS → compose.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from harness.gemma_client import GemmaClient
from harness.plan_builder import StemationPlanBuilder
from harness.tools.audio_tool import generate_voiceover
from harness.tools.compose_tool import compose_video_and_audio
from harness.tools.manim_tool import render_manim_code


class StemationPipeline:
    def __init__(
        self,
        model_name: str,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.llm = GemmaClient(model_name=model_name)
        self.plan_builder = StemationPlanBuilder(self.llm)
        self.log_callback = log_callback
        self.trace_history: List[Dict[str, str]] = []

    def _log(self, phase: str, message: str) -> None:
        entry = {"phase": phase, "message": message}
        self.trace_history.append(entry)
        if self.log_callback:
            self.log_callback(phase, message)
        else:
            print(f"[{phase}] {message}")

    def run(self, topic: str, max_repair_attempts: int = 2) -> Dict[str, Any]:
        self.trace_history.clear()

        self._log("SKILL_LOAD", "Loading Agent Skill 'stem-animator' (9:16 vertical rules)...")
        self._log("PLAN", f"Building narration + Manim plan for: '{topic}'...")

        plan, plan_source, model_used = self.plan_builder.build(topic)

        if plan_source == "llm":
            self._log("LLM_PLAN", f"Plan synthesized via Google GenAI ({model_used}).")
        else:
            self._log(
                "SKILL_TEMPLATE",
                "All models unavailable — using Agent Skill reference templates (full Manim render still runs).",
            )

        script = plan.get("narration_script", "")
        manim_code = plan.get("manim_code", "")
        next_topics = plan.get("next_topics", [])

        word_count = len(script.split()) if script else 0
        self._log("SCRIPT_READY", f"Narration script ready ({word_count} words).")
        self._log("CODE_READY", "Manim scene code ready for sandboxed compile.")

        self._log("TOOL_MANIM", "Invoking tool_render_manim (subprocess)...")
        render_res = render_manim_code(manim_code)

        attempts = 0
        while not render_res["success"] and attempts < max_repair_attempts:
            attempts += 1
            error_msg = render_res["error"] or "Unknown render error"
            self._log(
                "SELF_HEAL",
                f"Compiler error on attempt {attempts}. Sending traceback to LLM critic...",
            )
            manim_code = self.llm.self_heal_manim_code(manim_code, error_msg)
            self._log("SELF_HEAL", "Re-rendering with corrected Manim code...")
            render_res = render_manim_code(manim_code)

        if not render_res["success"]:
            self._log("ERROR", f"Render failed after {attempts} repair attempts.")
            return {
                "success": False,
                "error": render_res["error"],
                "trace": self.trace_history,
                "plan": plan,
                "plan_source": plan_source,
                "model_used": model_used,
            }

        raw_video_path = render_res["video_path"]
        self._log("RENDER_SUCCESS", f"Manim render complete: {raw_video_path}")

        self._log("TOOL_TTS", "Invoking tool_generate_tts (edge-tts)...")
        audio_res = generate_voiceover(script)

        if not audio_res["success"]:
            self._log("WARN", f"TTS failed ({audio_res['error']}). Returning silent video.")
            return {
                "success": True,
                "video_path": raw_video_path,
                "audio_path": None,
                "script": script,
                "manim_code": manim_code,
                "next_topics": next_topics,
                "trace": self.trace_history,
                "plan_source": plan_source,
                "model_used": model_used,
            }

        audio_path = audio_res["audio_path"]
        self._log("TTS_SUCCESS", f"Voiceover saved: {audio_path}")

        self._log("TOOL_COMPOSE", "Stitching 9:16 video + audio...")
        compose_res = compose_video_and_audio(raw_video_path, audio_path)
        final_video = compose_res["final_video_path"] if compose_res["success"] else raw_video_path
        if not compose_res["success"]:
            self._log("WARN", f"Compose used raw video only: {compose_res.get('error')}")
        self._log("COMPLETE", f"Stemation ready: {final_video}")

        return {
            "success": True,
            "video_path": final_video,
            "audio_path": audio_path,
            "script": script,
            "manim_code": manim_code,
            "next_topics": next_topics,
            "trace": self.trace_history,
            "plan_source": plan_source,
            "model_used": model_used,
        }
