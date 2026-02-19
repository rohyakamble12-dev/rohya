import wikipedia
import PyPDF2
import os
import json
import pandas as pd
from docx import Document

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
        """Reads text from various local file formats (PDF, TXT, DOCX, CSV, JSON)."""
        if not os.path.exists(file_path):
            return "Error: File path does not exist."

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                return VedaResearch._read_pdf(file_path)
            elif ext == '.docx':
                return VedaResearch._read_docx(file_path)
            elif ext == '.csv':
                return VedaResearch._read_csv(file_path)
            elif ext == '.json':
                return VedaResearch._read_json(file_path)
            else:
                # Default to plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(3000)
        except Exception as e:
            return f"Processing error for {ext.upper()}: {str(e)}"

    @staticmethod
    def _read_pdf(path):
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(min(len(reader.pages), 10)):
                text += reader.pages[i].extract_text() + "\n"
            return text[:4000]

    @staticmethod
    def _read_docx(path):
        doc = Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text[:4000]

    @staticmethod
    def _read_csv(path):
        df = pd.read_csv(path, nrows=20)
        return "CSV Data Snippet (Top 20 rows):\n" + df.to_string()

    @staticmethod
    def _read_json(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return "JSON Content Snippet:\n" + json.dumps(data, indent=2)[:3000]
