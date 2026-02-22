from deep_translator import GoogleTranslator
from veda.features.base import VedaPlugin, PermissionTier

class TranslatorPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("translate", self.translate, PermissionTier.SAFE)

    def translate(self, params):
        text = params.get("text", "")
        lang = params.get("language", "en")
        try:
            res = GoogleTranslator(source='auto', target=lang).translate(text)
            return f"Translated content: {res}"
        except: return "Translation node failure."
