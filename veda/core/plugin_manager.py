import importlib
import os
import inspect

class PluginManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.plugins = {}
        self.intent_map = {}

    def discover_and_load(self, plugin_dir="veda/features"):
        """Dynamically discovers and loads plugins from the specified directory."""
        if not os.path.exists(plugin_dir):
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"veda.features.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, "register_intents"):
                            plugin_instance = obj(self.assistant)
                            intents = plugin_instance.register_intents()
                            for intent, func in intents.items():
                                self.intent_map[intent] = func
                            self.plugins[module_name] = plugin_instance
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")

    def handle_intent(self, intent, params):
        """Routes the intent to the appropriate plugin function."""
        if intent in self.intent_map:
            return self.intent_map[intent](params)
        return None
