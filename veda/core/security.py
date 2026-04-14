import json
import os
from jsonschema import validate, ValidationError
from veda.features.base import PermissionTier
from veda.utils.logger import logger

class CapabilityManager:
    def __init__(self, config_path="veda/core/capabilities.json"):
        self.config_path = config_path
        self.config = {}
        # Delay registration until we are sure core modules are ready
        self._load_config()

    def _load_config(self):
        from veda.core.registry import registry
        if not registry.has("capability_manager"):
             registry.register("capability_manager", self)

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"Sovereign Policy: Load failure: {e}")
                self.config = self._get_default_policy()
        else:
            self.config = self._get_default_policy()
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def _get_default_policy(self):
        return {
            "roles": {
                "guest": {
                    "allowed_tiers": ["SAFE"],
                    "denied_intents": ["shell_isolated", "delete_item", "open_app"]
                },
                "operator": {
                    "allowed_tiers": ["SAFE", "LOW_RISK", "CONFIRM_REQUIRED"],
                    "denied_intents": ["shell_isolated"]
                },
                "admin": {
                    "allowed_tiers": ["SAFE", "LOW_RISK", "CONFIRM_REQUIRED", "ADMIN"],
                    "denied_intents": []
                }
            },
            "global_safe_mode": False
        }

    def validate_input(self, plugin, intent, params):
        """Bridge for validator calls."""
        return ContractValidator.validate_input(plugin, intent, params)

    def authorize(self, plugin, intent, params, current_role=None):
        if current_role is None:
             current_role = self.config.get("active_user_role", "operator")

        # Support both old rbac_model and new roles format
        if "rbac_model" in self.config and current_role in self.config["rbac_model"]:
             allowed_intents = self.config["rbac_model"][current_role]
             if "*" not in allowed_intents and intent not in allowed_intents:
                  return False, f"Role '{current_role}' not authorized for intent '{intent}'."
             return True, "Authorized via legacy RBAC."

        if "roles" not in self.config:
             return True, "Governance: Policy bypassed (config legacy)."

        role_policy = self.config["roles"].get(current_role, {})

        # 1. Deny List Check
        if intent in role_policy.get("denied_intents", []):
            return False, f"Role '{current_role}' is strictly prohibited from intent '{intent}'."

        # 2. Tier Authorization
        if intent not in plugin.intents: return False, "Unknown intent."
        tier = plugin.intents[intent]["tier"]

        allowed_tiers = role_policy.get("allowed_tiers", ["SAFE"])
        if tier.name not in allowed_tiers:
             return False, f"Permission Denied: Intent tier '{tier.name}' exceeds '{current_role}' authorization level."

        return True, "Authorized."

class ContractValidator:
    @staticmethod
    def validate_input(plugin, intent, params):
        """Zero-Trust: Enforces strict JSON Schema validation for all plugin inputs."""
        schema = plugin.get_intent_schema(intent)
        if not schema:
            if params: return False, "No tactical contract defined for this intent."
            return True, "Valid (No params)."

        try:
            validate(instance=params, schema=schema)
            return True, "Contract Valid."
        except ValidationError as e:
            logger.error(f"Contract Violation in {intent}: {e.message}")
            return False, e.message

    @staticmethod
    def validate_output(plugin, intent, result):
        return True

capabilities = CapabilityManager()
