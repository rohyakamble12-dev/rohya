import wikipedia
import PyPDF2
import os

class VedaResearch:
    @staticmethod
    def get_summary(topic):
        """Fetches a detailed summary from Wikipedia."""
        try:
            # Set language to English
            wikipedia.set_lang("en")
            # Search for the most relevant page
            search_results = wikipedia.search(topic)
            if not search_results:
                return "I couldn't find any specific encyclopedia entries for that topic."

            # Get the summary of the first result
            summary = wikipedia.summary(search_results[0], sentences=3)
            return f"According to available research on {search_results[0]}: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"That topic is broad. Could you be more specific? (e.g., {', '.join(e.options[:3])})"
        except Exception as e:
            return f"Research error: {str(e)}"

    @staticmethod
    def read_document(file_path):
        """Reads text from a local PDF or text file."""
        if not os.path.exists(file_path):
            return "File not found."

        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    # Read first 5 pages to avoid overloading
                    for i in range(min(len(reader.pages), 5)):
                        text += reader.pages[i].extract_text()
                    return text[:2000] # Return first 2000 chars
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(2000)
        except Exception as e:
            return f"Failed to read document: {str(e)}"
