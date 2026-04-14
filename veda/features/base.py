from enum import Enum
from abc import ABC, abstractmethod
from veda.utils.logger import logger

class PermissionTier(Enum):
    SAFE = 1             # No risk, no confirmation
    LOW_RISK = 2         # Informational but needs awareness
    CONFIRM_REQUIRED = 3 # High risk, requires user "Yes"
    ADMIN = 4            # System critical, requires override

class VedaPlugin(ABC):
    def __init__(self, assistant):
        self.assistant = assistant
        self.name = self.__class__.__name__
        self.intents = {} # intent_name: {method, tier, permissions, risk_level}
        self.setup()

    @abstractmethod
    def setup(self):
        """Mandatory setup logic for the plugin (e.g. intent registration)."""
        pass

    def register_intent(self, intent_name, method, tier=PermissionTier.SAFE, permissions=None, risk_level="Low",
                        input_schema=None, output_schema=None, undo_method=None, timeout=30, resource_load="Low"):
        self.intents[intent_name] = {
            "method": method,
            "tier": tier,
            "permissions": permissions or ["basic"],
            "risk_level": risk_level,
            "input_schema": input_schema or {"type": "object", "additionalProperties": False},
            "output_schema": output_schema or {"type": "string"},
            "undo_method": undo_method,
            "timeout": timeout,
            "resource_load": resource_load
        }
        logger.info(f"[{self.name}] Intent: {intent_name} | Tier: {tier.name} | Risk: {risk_level}")

    def get_intent_schema(self, intent):
        return self.intents.get(intent, {}).get("input_schema")

    def validate_params(self, intent, params):
        """Default validation. Should be overridden by subclasses for specific logic."""
        if not isinstance(params, dict):
            return False, "Params must be a dictionary."
        return True, "Valid."

    def predict_impact(self, intent, params):
        """Optional: Predicts the system impact of an action before execution."""
        return "Impact: Standard system operation."

    def execute(self, intent, params):
        if intent in self.intents:
            data = self.intents[intent]
            method = data["method"]
            tier = data["tier"]

            # Run validation
            valid, msg = self.validate_params(intent, params)
            if not valid:
                return f"Validation Error: {msg}", tier

            try:
                return method(params), tier
            except Exception as e:
                logger.error(f"Plugin Execution Error [{self.name}.{intent}]: {e}")
                return f"Error: {e}", tier
        return None, None
