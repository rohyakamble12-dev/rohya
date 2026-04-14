import wikipedia
import PyPDF2
import os
import json
import pandas as pd
from docx import Document
import zipfile
from veda.features.base import VedaPlugin, PermissionTier

class ResearchPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("deep_research", self.get_summary, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"], "additionalProperties": False})
        self.register_intent("read_doc", self.read_document_intent, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False})

    def get_summary(self, params):
        topic = params.get("topic")
        try:
            wikipedia.set_lang("en")
            res = wikipedia.summary(topic, sentences=3)
            return f"Strategic Research ({topic}): {res}"
        except Exception as e: return "Data missing in global archives."

    def read_document_intent(self, params):
        """Strategic Data Extraction: Actually reads PDF/Text/Docx files."""
        path = params.get("path")
        if not path or not os.path.exists(path): return "Source file inaccessible."

        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".pdf":
                text = ""
                with open(path, "rb") as f:
                    pdf = PyPDF2.PdfReader(f)
                    for page in pdf.pages[:10]: # Limit to first 10 pages for tactical speed
                        text += page.extract_text()
                return text[:5000]
            elif ext == ".docx":
                doc = Document(path)
                return "\n".join([p.text for p in doc.paragraphs])[:5000]
            elif ext in [".txt", ".py", ".json", ".csv"]:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(5000)
            else:
                return "File format currently outside strategic parameters."
        except Exception as e:
            return f"Extraction Failure: {e}"
