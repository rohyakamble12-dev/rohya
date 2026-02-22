from enum import Enum
from veda.utils.logger import logger

class PermissionTier(Enum):
    SAFE = 1             # No confirmation needed (e.g., time, weather)
    CONFIRM_REQUIRED = 2 # Requires user confirmation (e.g., delete, system sleep)
    ADMIN = 3           # Requires elevated/explicit confirmation (e.g., encryption, registry)

class VedaPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.name = self.__class__.__name__
        self.intents = {} # intent_name: (method, PermissionTier)

    def register_intent(self, intent_name, method, tier=PermissionTier.SAFE):
        self.intents[intent_name] = (method, tier)
        logger.info(f"Plugin {self.name} registered intent: {intent_name} [{tier.name}]")

    def execute(self, intent, params):
        if intent in self.intents:
            method, tier = self.intents[intent]
            return method(params), tier
        return None, None
