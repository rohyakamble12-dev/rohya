from veda.features.base import PermissionTier
from veda.utils.logger import logger
from veda.utils.events import bus, Events

class PluginManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.plugins = []
        self.intent_map = {} # intent_name: (plugin, method, tier)

    def load_plugin(self, plugin_instance):
        self.plugins.append(plugin_instance)
        for intent, (method, tier) in plugin_instance.intents.items():
            self.intent_map[intent] = (plugin_instance, method, tier)
        logger.info(f"Loaded plugin: {plugin_instance.name}")

    def execute_intent(self, intent, params):
        if intent not in self.intent_map:
            return f"Error: Intent '{intent}' not recognized by any plugin.", PermissionTier.SAFE

        plugin, method, tier = self.intent_map[intent]

        # Check if confirmation is needed (handled by Assistant/GUI)
        if tier != PermissionTier.SAFE:
            # We return the intent info and the tier, the Assistant will handle the Gating
            return (method, params), tier

        try:
            result = method(params)
            bus.publish(Events.ACTION_COMPLETED, {"intent": intent, "result": result})
            return result, tier
        except Exception as e:
            logger.error(f"Execution error in {plugin.name}.{intent}: {e}")
            return f"System Error: {str(e)}", tier
