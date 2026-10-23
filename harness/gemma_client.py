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
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{system_instruction}\n\n---\nUSER REQUEST:\n{user_prompt}"
            )
        except Exception as e:
            # If specified gemma preview model is unavailable on this key, attempt fallback
            if "gemma-4" in self.model_name:
                print(f"[Harness Notice] '{self.model_name}' returned error: {e}. Attempting fallback...")
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_instruction}\n\n---\nUSER REQUEST:\n{user_prompt}"
                )
            else:
                raise e
                
        return self._clean_json_response(response.text)

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
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=fix_prompt
        )
        
        fixed_text = response.text.strip()
        if fixed_text.startswith("```"):
            lines = fixed_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            fixed_text = "\n".join(lines).strip()
            
        return fixed_text
