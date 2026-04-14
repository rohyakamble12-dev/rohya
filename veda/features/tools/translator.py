from deep_translator import GoogleTranslator
from veda.features.base import VedaPlugin, PermissionTier

class TranslatorPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("translate", self.translate, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"text": {"type": "string"}, "dest": {"type": "string"}}, "required": ["text", "dest"], "additionalProperties": False})

    def translate(self, params):
        text = params.get("text", "")
        lang = params.get("dest", "en")
        try:
            res = GoogleTranslator(source='auto', target=lang).translate(text)
            return f"Translated content: {res}"
        except Exception as e: return "Translation node failure."
