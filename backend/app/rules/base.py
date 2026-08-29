from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.rule_finding import RuleFinding

class BaseRule(ABC):
    rule_id: str
    rule_name: str
    description: str

    @abstractmethod
    def evaluate(
        self,
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> RuleFinding:
        """
        Executes deterministic network verification logic.
        Returns a structured RuleFinding.
        """
        pass
