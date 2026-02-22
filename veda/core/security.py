import json
import os
from veda.features.base import PermissionTier
from veda.utils.logger import logger
from veda.core.registry import registry

class CapabilityManager:
    def __init__(self, policy_path="veda/core/capabilities.json"):
        self.policy_path = policy_path
        self.policy = self._load_policy()
        registry.register("capability_manager", self)

    def _load_policy(self):
        try:
            if os.path.exists(self.policy_path):
                with open(self.policy_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Policy load failed: {e}")
        return {"global_policy": "DEFAULT", "blocked_intents": []}

    def authorize(self, intent, tier, params):
        if intent in self.policy.get("blocked_intents", []):
            return False, f"Protocol Violation: {intent} is restricted by global policy."

        if tier == PermissionTier.SAFE:
            return True, "Authorized."

        if tier == PermissionTier.CONFIRM_REQUIRED:
            return False, "Verification required."

        if tier == PermissionTier.ADMIN:
            return False, "Administrative authorization required."

        return False, "Access denied."

    def validate_params(self, intent, params):
        return True, "Valid."

# Singleton instance
capabilities = CapabilityManager()
