"""
Gemma 4 Client Wrapper using Google GenAI SDK (google-genai)
"""
import os
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

from harness.context import SkillContextLoader
from harness.models import (
    DEFAULT_MODEL,
    GENERATION_FALLBACKS,
    SELF_HEAL_FALLBACKS,
    model_attempt_order,
)

load_dotenv()


class GemmaClient:
    def __init__(self, model_name: str = DEFAULT_MODEL, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment or .env file. "
                "Please add GEMINI_API_KEY to your .env file."
            )

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=180_000),
        )
        self.model_name = model_name
        self.context_loader = SkillContextLoader()

    def _clean_json_response(self, text: str) -> Dict[str, Any]:
        """Strips markdown code fences and parses raw JSON safely."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse valid JSON from Gemma response:\n{text}")

    def _generate_text(self, models: List[str], contents: str) -> Tuple[str, str]:
        last_error: Optional[Exception] = None
        for m in models:
            try:
                response = self.client.models.generate_content(model=m, contents=contents)
                if response and response.text:
                    return response.text, m
            except Exception as e:
                last_error = e
                print(f"[Harness Notice] Model '{m}' unavailable ({e}). Trying fallback...")
        raise RuntimeError(f"All model attempts failed. Last error: {last_error}")

    def generate_stemation(self, topic: str) -> Tuple[Dict[str, Any], str]:
        """
        Orchestrates the LLM to produce narration script, Manim code, and follow-up topics.
        Returns (plan_dict, model_id_used).
        """
        system_instruction = self.context_loader.build_system_prompt()
        prompt = f"{system_instruction}\n\nSTEM TOPIC TO ANIMATE: {topic}"

        models = model_attempt_order(self.model_name, GENERATION_FALLBACKS)
        text, model_used = self._generate_text(models, prompt)
        return self._clean_json_response(text), model_used

    def self_heal_manim_code(self, broken_code: str, error_traceback: str) -> str:
        """Feeds compiler traceback back into the model to fix errors automatically."""
        fix_prompt = (
            f"You are the Manim code compiler critic for the 'stem-animator' skill.\n"
            f"The following Manim Python code produced a rendering error:\n\n"
            f"```python\n{broken_code}\n```\n\n"
            f"ERROR TRACEBACK:\n{error_traceback}\n\n"
            f"Please fix the code. Return ONLY the corrected Python code, without explanations or fences."
        )

        models = model_attempt_order(self.model_name, SELF_HEAL_FALLBACKS)
        try:
            fixed_text, _model = self._generate_text(models, fix_prompt)
            fixed_text = fixed_text.strip()
        except RuntimeError:
            return broken_code

        if fixed_text.startswith("```"):
            lines = fixed_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            fixed_text = "\n".join(lines).strip()
        return fixed_text
