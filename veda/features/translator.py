from deep_translator import GoogleTranslator
from veda.features.base import VedaPlugin, PermissionTier

class TranslatorPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("translate", self.translate, PermissionTier.SAFE)

    def translate(self, params):
        text = params.get("text", "")
        lang = params.get("language", "en")
        try:
            res = GoogleTranslator(source='auto', target=lang).translate(text)
            return f"Translated: {res}"
        except Exception as e:
            return f"Translation error: {e}"
