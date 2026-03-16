try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

class KnowledgePlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "wiki_search": self.search_wikipedia
        }

    def search_wikipedia(self, params):
        if not WIKIPEDIA_AVAILABLE:
            return "Knowledge link offline: wikipedia library not installed."
        query = params.get("query", "")
        if not query: return "Topic missing."

        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Intelligence link conflicted. Too many results for {query}. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"I couldn't find any intelligence data on {query}."
        except Exception:
            return "Knowledge link failed."
