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
        """Constructs the comprehensive system prompt for Gemma 4."""
        skill_data = self.load_skill()
        skill_name = skill_data["metadata"].get("name", "stem-animator")
        
        prompt = (
            f"You are an expert STEM educator and Manim animation software engineer.\n"
            f"You are operating under the Agent Skill '{skill_name}'.\n\n"
            f"SKILL SPECIFICATION & RULES:\n"
            f"{skill_data['instructions']}\n\n"
            f"CRITICAL REQUIREMENTS:\n"
            f"1. You MUST respond with ONLY a single valid JSON object, without backticks or markdown code fences.\n"
            f"2. The JSON keys must be exactly: 'topic', 'narration_script', 'manim_code', and 'next_topics'.\n"
            f"3. 'manim_code' must be complete, executable Python code with Scene class named 'StemationScene'.\n"
            f"4. The animation must be vertical (1080x1920) and duration between 15 and 25 seconds.\n"
            f"5. 'next_topics' must be an array of 3 real, sequential follow-up STEM concepts.\n"
        )
        return prompt
