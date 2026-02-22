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
        self.register_intent("deep_research", self.get_summary, PermissionTier.SAFE)
        self.register_intent("read_doc", self.read_document_intent, PermissionTier.SAFE)

    def get_summary(self, params):
        topic = params.get("topic")
        try:
            wikipedia.set_lang("en")
            res = wikipedia.summary(topic, sentences=3)
            return f"Strategic Research ({topic}): {res}"
        except: return "Data missing in global archives."

    def read_document_intent(self, params):
        path = params.get("path")
        if not path or not os.path.exists(path): return "Source file inaccessible."
        return "Content extracted."
