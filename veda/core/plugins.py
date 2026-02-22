from veda.features.base import PermissionTier
from veda.utils.logger import logger
from veda.utils.events import bus, Events
from veda.core.registry import registry

class PluginManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.plugins = {}
        self.intent_map = {}
        registry.register("plugin_manager", self)

    def load_plugin(self, plugin_instance):
        name = plugin_instance.name
        self.plugins[name] = plugin_instance
        for intent, (method, tier) in plugin_instance.intents.items():
            self.intent_map[intent] = (plugin_instance, method, tier)
        logger.info(f"Loaded Plugin: {name} ({len(plugin_instance.intents)} intents)")

    def execute_intent(self, intent, params):
        if intent not in self.intent_map:
            return f"Intent '{intent}' unmapped.", PermissionTier.SAFE

        plugin, method, tier = self.intent_map[intent]

        if tier != PermissionTier.SAFE:
            return (method, params), tier

        try:
            result = method(params)
            bus.publish(Events.ACTION_COMPLETED, {"intent": intent, "result": result})
            return result, tier
        except Exception as e:
            logger.error(f"Plugin Error [{plugin.name}.{intent}]: {e}")
            return f"Execution failure: {e}", tier

    def get_plugin(self, name):
        return self.plugins.get(name)

    def get_plugin_for_intent(self, intent):
        if intent in self.intent_map:
            return self.intent_map[intent][0]
        return None
