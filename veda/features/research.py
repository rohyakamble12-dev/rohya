import wikipedia
import PyPDF2
import os
import json
import pandas as pd
from docx import Document
import zipfile
import tempfile
import shutil

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
        """Reads text from various local file formats (PDF, TXT, DOCX, CSV, JSON, ZIP)."""
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
            elif ext == '.zip':
                return VedaResearch._read_zip(file_path)
            else:
                # Optimized plain text reading for large files
                return VedaResearch._read_text_optimized(file_path)
        except Exception as e:
            return f"Processing error for {ext.upper()}: {str(e)}"

    @staticmethod
    def _read_text_optimized(path):
        file_size = os.path.getsize(path)
        max_read = 5000
        if file_size <= max_read:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            # Sample start and end for large files
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                start = f.read(2500)
                f.seek(file_size - 2500)
                end = f.read(2500)
                return f"[Large File Sample - Start]:\n{start}\n\n[... content truncated ...]\n\n[Sample - End]:\n{end}"

    @staticmethod
    def _read_zip(path):
        summary = f"ZIP Archive: {os.path.basename(path)}\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                # Get list of files
                file_list = zip_ref.namelist()
                summary += f"Contains {len(file_list)} items.\n\n"

                # Filter for interesting documents
                interesting = [f for f in file_list if f.lower().endswith(('.pdf', '.txt', '.docx', '.csv', '.json'))]

                for f_name in interesting[:5]: # Process first 5 docs to avoid overload
                    zip_ref.extract(f_name, tmpdir)
                    extracted_path = os.path.join(tmpdir, f_name)
                    content = VedaResearch.read_document(extracted_path)
                    summary += f"--- Content of {f_name} ---\n{content[:1000]}\n\n"

                if len(interesting) > 5:
                    summary += f"... and {len(interesting) - 5} more documents found in archive."
        return summary

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
