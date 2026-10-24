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
            # Default to skills/stem-animator relative to backend or project root
            base_dir = Path(__file__).resolve().parent.parent
            candidate = base_dir / "skills" / "stem-animator"
            if not candidate.exists():
                candidate = base_dir.parent / "skills" / "stem-animator"
            self.skill_dir = candidate
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
        """Constructs a clean, high-impact system prompt for Gemma 4 using SKILL.md."""
        skill_data = self.load_skill()
        skill_instructions = skill_data.get("instructions", "")
        
        prompt = (
            "You are an expert STEM educator and Manim animation software engineer.\n"
            "Your mission: synthesize a pedagogically crystal-clear, highly engaging vertical (9:16) educational animation\n"
            "that completely and intuitively conveys ONE SINGLE STEM CONCEPT in 35 to 50 seconds (STRICTLY UNDER 60 SECONDS).\n\n"
            "=== AGENT SKILL SPECIFICATION (stem-animator) ===\n"
            f"{skill_instructions}\n"
            "=================================================\n\n"
            "MANDATORY EXECUTION DIRECTIVES:\n"
            "1. HOOK & ENGAGEMENT: Narration MUST start with an irresistible curiosity question or surprising real-world hook.\n"
            "   Directly engage the viewer throughout ('Notice what happens...', 'Look at this pattern...').\n"
            "2. LENGTH & TIMING: Video must be 35 to 50 seconds (UNDER 60 SECONDS). Narration script must be 75 to 110 words.\n"
            "   Manim scene must have 4-6 sequential animated beats with self.wait(1.5) pauses to match the ~40s voiceover.\n"
            "3. Canvas: config.pixel_width=1080, config.pixel_height=1920, config.frame_width=9.0, config.frame_height=16.0, background_color='#0F172A'.\n"
            "4. Coordinate bounds: x in [-3.6, 3.6], y in [-6.0, 6.0]. Never let text or shapes overflow the screen.\n"
            "5. Portability: Use Text() with clean unicode symbols for math/equations (NEVER MathTex or Tex) to guarantee rendering without LaTeX.\n"
            "6. Scene class MUST be named StemationScene(Scene).\n"
            "7. Output MUST be ONLY a single valid JSON object without markdown code fences:\n"
            "   {\n"
            '     "topic": "<Concept Name>",\n'
            '     "narration_script": "<75-110 word engaging script with curiosity hook, step-by-step guidance, and payoff>",\n'
            '     "manim_code": "<100% executable Python Manim script with 35-50s runtime>",\n'
            '     "next_topics": ["<Next Topic 1>", "<Next Topic 2>", "<Next Topic 3>"]\n'
            "   }\n"
        )
        return prompt
