import wikipedia
import PyPDF2
import os
import json
import pandas as pd
from docx import Document
import zipfile
import tempfile
from veda.features.base import VedaPlugin, PermissionTier

class ResearchPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("deep_research", self.get_summary, PermissionTier.SAFE)
        self.register_intent("read_doc", self.read_document_intent, PermissionTier.SAFE)

    def get_summary(self, params):
        topic = params.get("topic")
        if not topic: return "State a research topic."
        try:
            wikipedia.set_lang("en")
            results = wikipedia.search(topic)
            if not results: return "No entries found."
            summary = wikipedia.summary(results[0], sentences=3)
            return f"Research result ({results[0]}): {summary}"
        except Exception as e:
            return f"Research error: {e}"

    def read_document_intent(self, params):
        path = params.get("path")
        if not path: return "No path provided."
        return self.read_document(path)

    def read_document(self, file_path):
        if not os.path.exists(file_path): return "File not found."
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf': return self._read_pdf(file_path)
            elif ext == '.docx': return self._read_docx(file_path)
            elif ext == '.csv': return self._read_csv(file_path)
            elif ext == '.json': return self._read_json(file_path)
            elif ext == '.zip': return self._read_zip(file_path)
            else: return self._read_text_optimized(file_path)
        except Exception as e:
            return f"Error reading {ext}: {e}"

    def _read_text_optimized(self, path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(5000)

    def _read_pdf(self, path):
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "".join([p.extract_text() for p in reader.pages[:5]])
            return text[:4000]

    def _read_docx(self, path):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs[:50]])[:4000]

    def _read_csv(self, path):
        df = pd.read_csv(path, nrows=10)
        return df.to_string()

    def _read_json(self, path):
        with open(path, 'r') as f:
            return json.dumps(json.load(f), indent=2)[:3000]

    def _read_zip(self, path):
        with zipfile.ZipFile(path, 'r') as z:
            return "Archive contents: " + ", ".join(z.namelist()[:20])
