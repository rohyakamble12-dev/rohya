from deep_translator import GoogleTranslator

class VedaTranslator:
    @staticmethod
    def translate_text(text, target_lang='en'):
        """Translates text to the target language."""
        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            translation = translator.translate(text)
            return translation
        except Exception as e:
            return f"Translation failed: {str(e)}"

    @staticmethod
    def get_supported_languages():
        """Returns a list of commonly used language codes."""
        return {
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "chinese": "zh-CN",
            "hindi": "hi",
            "japanese": "ja",
            "russian": "ru",
            "italian": "it"
        }
