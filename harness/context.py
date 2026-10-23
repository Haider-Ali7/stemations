"""
Context and Skill Loader for Stemations Model Harness
Adheres to the Agent Skill Open Standard
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

class SkillContextLoader:
    def __init__(self, skill_dir: Optional[str] = None):
        if skill_dir is None:
            # Default to skills/stem-animator relative to project root
            base_dir = Path(__file__).resolve().parent.parent
            self.skill_dir = base_dir / "skills" / "stem-animator"
        else:
            self.skill_dir = Path(skill_dir)
            
        self.skill_file = self.skill_dir / "SKILL.md"
        self.templates_dir = self.skill_dir / "templates"
        
    def load_skill(self) -> Dict[str, Any]:
        """Loads and parses the SKILL.md specification and any templates."""
        if not self.skill_file.exists():
            raise FileNotFoundError(f"Agent Skill file not found: {self.skill_file}")
            
        raw_text = self.skill_file.read_text(encoding="utf-8")
        
        # Parse YAML frontmatter if present
        frontmatter = {}
        content = raw_text
        if raw_text.startswith("---"):
            parts = raw_text.split("---", 2)
            if len(parts) >= 3:
                yaml_block = parts[1].strip()
                content = parts[2].strip()
                for line in yaml_block.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        frontmatter[k.strip()] = v.strip().strip('"').strip("'")
                        
        templates = {}
        if self.templates_dir.exists():
            for t_file in self.templates_dir.glob("*.py"):
                templates[t_file.stem] = t_file.read_text(encoding="utf-8")
                
        return {
            "metadata": frontmatter,
            "instructions": content,
            "templates": templates
        }

    def build_system_prompt(self) -> str:
        """Constructs a clean, high-impact system prompt for Gemma 4."""
        prompt = (
            "You are an expert STEM educator and Manim animation software engineer.\n"
            "Generate a vertical (9:16) educational animation for the requested STEM concept.\n\n"
            "STRICT RULES:\n"
            "1. Output MUST be ONLY a single valid JSON object, with NO markdown code fences around the JSON.\n"
            "2. JSON Keys required:\n"
            "   - 'topic': Concept name string\n"
            "   - 'narration_script': Concise 25-35 word spoken script (~15-20s duration)\n"
            "   - 'manim_code': Self-contained executable Python code with Scene subclass named 'StemationScene'\n"
            "   - 'next_topics': Array of 3 sequential STEM topics to learn next\n\n"
            "MANIM RULES:\n"
            "- Canvas: config.pixel_width=1080, config.pixel_height=1920, config.frame_width=9.0, config.frame_height=16.0\n"
            "- Background: '#0F172A', safe zone x in [-3.8, 3.8], y in [-6.0, 6.0]\n"
            "- Header text around y=5.5 to 6.0, main visual center around y=0.5 to 1.5, explanation around y=-3.5 to -4.5\n"
            "- Use Text() with clean unicode for formulas (avoid latex compilation dependency)\n"
            "- Smooth animations using Create, Transform, FadeIn, FadeOut, run_time 1.0 to 1.5s\n"
            "- End scene with self.wait(2)\n"
        )
        return prompt
