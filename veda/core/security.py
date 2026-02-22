from veda.features.base import PermissionTier
from veda.utils.logger import logger
from veda.core.registry import registry

class CapabilityManager:
    def __init__(self):
        self.registry = registry
        registry.register("capability_manager", self)

    def authorize(self, intent, tier, params):
        """Determines if an intent execution is authorized based on tier and context."""
        if tier == PermissionTier.SAFE:
            return True, "Authorized."

        if tier == PermissionTier.CONFIRM_REQUIRED:
            return False, f"Verification required for {intent}."

        if tier == PermissionTier.ADMIN:
            return False, f"Administrative override required for {intent}."

        return False, "Unknown permission tier."

    def validate_params(self, intent, params):
        """Sanitizes and validates parameters for a given intent."""
        # This could be expanded with specific schemas per intent
        if not isinstance(params, dict):
            return False, "Invalid parameter format."
        return True, "Valid."

# Singleton instance
capabilities = CapabilityManager()
