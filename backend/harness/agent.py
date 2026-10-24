"""
Stemations Autonomous Orchestrator Agent (facade over StemationPipeline).
"""
from typing import Any, Callable, Dict, List, Optional

from harness.models import DEFAULT_MODEL
from harness.pipeline import StemationPipeline


class StemationsAgent:
    """Coordinates Agent Skill ingestion, LLM reasoning, tools, and self-healing."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self._pipeline = StemationPipeline(model_name=model_name, log_callback=log_callback)

    @property
    def trace_history(self) -> List[Dict[str, str]]:
        return self._pipeline.trace_history

    def run(self, topic: str, max_repair_attempts: int = 2) -> Dict[str, Any]:
        return self._pipeline.run(topic, max_repair_attempts=max_repair_attempts)
