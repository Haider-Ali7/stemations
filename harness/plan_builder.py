"""
Builds a Stemation plan (script + Manim code + curriculum) from the LLM or Agent Skill templates.
Template path still runs the full render/TTS pipeline — it is only used when every model fails.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from harness.context import SkillContextLoader
from harness.gemma_client import GemmaClient


def _escape_manim_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class StemationPlanBuilder:
    def __init__(self, llm: GemmaClient, loader: SkillContextLoader | None = None):
        self.llm = llm
        self.loader = loader or SkillContextLoader()

    def build(self, topic: str) -> Tuple[Dict[str, Any], str, str | None]:
        """
        Returns (plan, plan_source, model_used).
        plan_source: 'llm' | 'skill_template'
        """
        try:
            plan, model_used = self.llm.generate_stemation(topic)
            return plan, "llm", model_used
        except RuntimeError as exc:
            plan = self._plan_from_skill_templates(topic, str(exc))
            return plan, "skill_template", None

    def _plan_from_skill_templates(self, topic: str, llm_error: str) -> Dict[str, Any]:
        skill = self.loader.load_skill()
        templates: Dict[str, str] = skill.get("templates", {})
        topic_lower = topic.lower()

        math_keys = ("theorem", "pythag", "geometry", "triangle", "equation", "proof", "calculus")
        if any(k in topic_lower for k in math_keys) and "math_template" in templates:
            manim_code = templates["math_template"]
            manim_code = manim_code.replace(
                'Text("Pythagorean Theorem"',
                f'Text("{_escape_manim_string(topic[:48])}"',
                1,
            )
            next_topics = [
                "Triangle Similarity",
                "Distance Formula on a Plane",
                "Trigonometric Ratios",
            ]
            script = (
                f"How did ancient builders lay out perfect square corners before laser measures existed? "
                f"They used the geometric power of the {topic}! Look closely at this right-angled triangle. "
                f"When you build squares on both perpendicular legs, their combined surface area exactly matches "
                f"the square built on the hypotenuse. In algebraic terms: a squared plus b squared equals c squared. "
                f"This fundamental law forms the bedrock of modern physics, GPS navigation, and engineering!"
            )
        elif "algorithm_template" in templates:
            manim_code = templates["algorithm_template"]
            manim_code = manim_code.replace(
                'Text("Binary Search"',
                f'Text("{_escape_manim_string(topic[:48])}"',
                1,
            )
            next_topics = [
                "Linear Search vs Binary Search",
                "Merge Sort Visualization",
                "Big-O Notation Basics",
            ]
            script = (
                f"What if you had to find one specific person in a phone book of one billion names? "
                f"Checking one by one could take your entire lifetime. But with {topic}, you can do it in thirty steps! "
                f"Because the list is sorted, we jump straight to the middle. If our target is larger, we discard the entire "
                f"lower half in a single leap. By repeatedly halving the search space, divide and conquer solves massive problems "
                f"in logarithmic time!"
            )
        else:
            raise RuntimeError(f"No skill templates available after LLM failure: {llm_error}")

        script = re.sub(r"\s+", " ", script).strip()
        return {
            "topic": topic,
            "narration_script": script,
            "manim_code": manim_code,
            "next_topics": next_topics,
            "fallback_reason": llm_error,
        }
