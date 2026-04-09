from veda.features.base import PermissionTier
from veda.utils.logger import logger
from veda.utils.events import bus, Events
from veda.core.registry import registry

import importlib
import inspect
import os
import sys

# Tactical Plugin Mapping for Process Isolation
PLUGIN_REGISTRY = {}

def discover_and_load():
    """Isolated discovery: Allows child processes to autonomously map tactical modules."""
    global PLUGIN_REGISTRY
    plugin_dir = os.path.join(os.path.dirname(__file__), "..", "features")
    if not os.path.exists(plugin_dir):
        return

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"veda.features.{filename[:-3]}"
            try:
                # Ensure the module is loaded or reloaded
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    # Robust check for VedaPlugin inheritance
                    if inspect.isclass(obj) and any(base.__name__ == "VedaPlugin" for base in obj.__mro__):
                        PLUGIN_REGISTRY[obj.__name__] = obj
            except Exception as e:
                logger.warning(f"Sovereign Discovery: Failed to load {module_name}: {e}")

def get_plugin_class(name):
    if not PLUGIN_REGISTRY: discover_and_load()
    return PLUGIN_REGISTRY.get(name)

def register_plugin_class(name, cls):
    PLUGIN_REGISTRY[name] = cls

class PluginManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.plugins = {}
        self.intent_map = {}
        registry.register("plugin_manager", self)

    def load_plugin(self, plugin_instance):
        name = plugin_instance.name
        self.plugins[name] = plugin_instance
        register_plugin_class(name, plugin_instance.__class__)
        for intent, data in plugin_instance.intents.items():
            method_name = data["method"].__name__
            tier = data["tier"]
            self.intent_map[intent] = (plugin_instance, method_name, tier)
        logger.info(f"Loaded Plugin: {name} ({len(plugin_instance.intents)} intents)")

    def is_admin_intent(self, intent):
        if intent not in self.intent_map: return False
        return self.intent_map[intent][2] == PermissionTier.ADMIN

    def should_confirm(self, intent, params):
        """Security Policy check to see if human-in-the-loop is required."""
        if intent not in self.intent_map: return False, "Unknown intent."
        plugin, _, tier = self.intent_map[intent]

        # 1. Tier-based gating
        if tier in [PermissionTier.CONFIRM_REQUIRED, PermissionTier.ADMIN]:
             return True, "Mandatory Tactical Confirmation."

        # 2. Advanced Policy (e.g. risk level, global safe-mode)
        from veda.core.security import capabilities
        authorized, reason = capabilities.authorize(plugin, intent, params)
        if not authorized:
            return True, reason

        return False, "Clear."

    def execute_intent_direct(self, intent, params):
        """Direct execution without security gating (assumed gated by Assistant)."""
        if intent not in self.intent_map:
            return f"Error: Intent '{intent}' unmapped."

        plugin, method_name, _ = self.intent_map[intent]

        try:
            # Post-gating parameter scrubbing/validation
            valid, msg = plugin.validate_params(intent, params)
            if not valid: return f"Error: {msg}"

            # If this is called in the same process
            method = getattr(plugin, method_name)
            result = method(params)

            # Post-Execution Contract Validation
            from veda.core.security import ContractValidator
            ContractValidator.validate_output(plugin, intent, result)

            bus.publish(Events.ACTION_COMPLETED, {"intent": intent, "result": result})
            return result
        except Exception as e:
            logger.error(f"Plugin Fault [{plugin.name}.{intent}]: {e}")
            raise e

    def get_plugin(self, name):
        return self.plugins.get(name)

    def get_plugin_for_intent(self, intent):
        if intent in self.intent_map:
            return self.intent_map[intent][0]

        # Deep Search Trigger: If intent not found, attempt a tactical re-discovery
        logger.warning(f"Tactical Miss: Intent '{intent}' not in primary registry. Re-scanning feature sectors.")
        self.assistant._initialize_plugins()

        if intent in self.intent_map:
            return self.intent_map[intent][0]

        return None
