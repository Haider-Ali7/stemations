"""
Gemma 4 Client Wrapper using Google GenAI SDK (google-genai)
"""
import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from harness.context import SkillContextLoader

load_dotenv()

class GemmaClient:
    def __init__(self, model_name: str = "gemma-4-26b-a4b-it", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment or .env file. "
                "Please add GEMINI_API_KEY to your .env file."
            )
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        self.context_loader = SkillContextLoader()
        
    def _clean_json_response(self, text: str) -> Dict[str, Any]:
        """Strips markdown code fences and parses raw JSON safely."""
        text = text.strip()
        # Remove markdown code fences if present
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
            # Fallback regex extraction of json object
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse valid JSON from Gemma response:\n{text}")

    def generate_stemation(self, topic: str) -> Dict[str, Any]:
        """
        Orchestrates Gemma 4 to produce:
        1. Narration script (~30 words)
        2. Executable Manim Python code (vertical 9:16)
        3. 3 Recommended sequential follow-up topics
        """
        system_instruction = self.context_loader.build_system_prompt()
        user_prompt = (
            f"Generate a 30-second vertical Manim explainer video for the STEM topic:\n"
            f"TOPIC: {topic}\n\n"
            f"Ensure the animation is visually intuitive, uses the 'stem-animator' safe coordinates, "
            f"and include 3 sequential follow-up topics to deepen student learning."
        )
        
        prompt = f"{system_instruction}\n\nSTEM TOPIC TO ANIMATE: {topic}"
        
        priority_models = [
            self.model_name,
            "gemma-4-26b-a4b-it",
            "gemma-4-31b-it",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash",
            "gemini-3.8-flash"
        ]
        models_to_try = []
        for m in priority_models:
            if m not in models_to_try:
                models_to_try.append(m)
            
        last_error = None
        for m in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    return self._clean_json_response(response.text)
            except Exception as e:
                last_error = e
                print(f"[Harness Notice] Model '{m}' returned: {e}. Trying next available model...")
                
        raise RuntimeError(f"All model attempts failed. Last error: {last_error}")

    def self_heal_manim_code(self, broken_code: str, error_traceback: str) -> str:
        """
        Feeds compiler traceback back into Gemma to fix errors automatically.
        """
        fix_prompt = (
            f"You are the Manim code compiler critic for the 'stem-animator' skill.\n"
            f"The following Manim Python code produced a rendering error:\n\n"
            f"```python\n{broken_code}\n```\n\n"
            f"ERROR TRACEBACK:\n{error_traceback}\n\n"
            f"Please fix the code. Return ONLY the corrected Python code, without explanations or fences."
        )
        
        models_to_try = [
            self.model_name,
            "gemma-4-26b-a4b-it",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash"
        ]
        
        for m in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m,
                    contents=fix_prompt
                )
                if response and response.text:
                    fixed_text = response.text.strip()
                    if fixed_text.startswith("```"):
                        lines = fixed_text.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        fixed_text = "\n".join(lines).strip()
                    return fixed_text
            except Exception as e:
                print(f"[Harness Notice] Self-heal model '{m}' returned: {e}. Trying fallback...")
                
        return broken_code
