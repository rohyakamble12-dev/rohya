from veda.features.base import VedaPlugin, PermissionTier

class HelpPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("help", self.get_help, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

    def get_help(self, params):
        """Dynamic Tactical Help."""
        intents = list(self.assistant.plugins.intent_map.keys())
        # Provide a stratified list
        core = ["open_app", "calculate", "todo_add", "web_search", "sys_health"]
        advanced = ["vision_analyze", "deep_research", "clean_slate", "shell_isolated"]

        msg = f"Veda Core Protocol Active. {len(intents)} intents registered.\n\n"
        msg += f"Tactical Ops: {', '.join(core)}\n"
        msg += f"Strategic Ops: {', '.join(advanced)}\n"
        msg += "Sir, just state your requirement clearly and I will orchestrate the sequence."
        return msg
