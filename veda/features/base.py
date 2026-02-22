from enum import Enum
from abc import ABC, abstractmethod
from veda.utils.logger import logger

class PermissionTier(Enum):
    SAFE = 1
    CONFIRM_REQUIRED = 2
    ADMIN = 3

class VedaPlugin(ABC):
    def __init__(self, assistant):
        self.assistant = assistant
        self.name = self.__class__.__name__
        self.intents = {} # intent_name: (method, PermissionTier)
        self.setup()

    @abstractmethod
    def setup(self):
        """Mandatory setup logic for the plugin (e.g. intent registration)."""
        pass

    def register_intent(self, intent_name, method, tier=PermissionTier.SAFE):
        self.intents[intent_name] = (method, tier)
        logger.info(f"[{self.name}] Registered: {intent_name} ({tier.name})")

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
            method, tier = self.intents[intent]

            # Run validation
            valid, msg = self.validate_params(intent, params)
            if not valid:
                return f"Validation Error: {msg}", tier

            return method(params), tier
        return None, None
