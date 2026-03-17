import ollama
import json
import logging
import subprocess
import time
import re
import os

class VedaBrain:
    def __init__(self, model="qwen2.5:3b"):
        self.model = model
        self.system_prompt = (
            "You are Veda, an advanced artificial intelligence inspired by JARVIS. "
            "Your personality is professional, concise, and highly efficient. "
            "You prioritize tactical execution over conversational filler. "
            "Always maintain your identity as a local system interface."
        )

    def ensure_ollama(self):
        try:
            ollama.list()
        except Exception:
            logging.info("[SYSTEM]: Ollama not detected. Attempting auto-launch...")
            subprocess.Popen(["ollama", "serve"], shell=True)
            time.sleep(5)

    def classify_intent(self, text):
        """Classifies intent BEFORE full LLM processing to optimize speed."""
        text = text.lower().strip()

        patterns = {
            "command": r"^(open|close|set|brightness|volume|screenshot|lock|shutdown|restart|play|pause|next|previous)",
            "calculation": r"^[0-9+\-*/().\s^]+$",
            "search": r"^(search|deep research|summarize|wikipedia|who is|what is)",
            "productivity": r"^(add todo|show todo|complete todo|remind|weather)"
        }

        for intent, pattern in patterns.items():
            if re.search(pattern, text):
                return intent
        return "conversation"

    def chat(self, user_input, history):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            logging.error(f"Neural link failed: {e}")
            return "Neural link unstable, Operator. Operating in restricted tactical mode."

    def extract_params(self, user_input):
        """Uses LLM to extract JSON parameters for commands."""
        prompt = (
            "Analyze the command and extract parameters into a raw JSON object. "
            "Include 'intent' and 'params'. "
            f"Command: \"{user_input}\""
        )
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "Parameter Extractor. Raw JSON only."},
                          {"role": "user", "content": prompt}]
            )
            content = response['message']['content']
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"intent": "none", "params": {}}
        except:
            return {"intent": "none", "params": {}}
