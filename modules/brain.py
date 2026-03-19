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
            # Check if ollama is reachable with a short timeout
            # Note: ollama-python doesn't expose timeout easily in list()
            # but we can assume if it fails it's down.
            ollama.list()
            return True
        except Exception:
            logging.info("[SYSTEM]: Ollama not detected. Attempting auto-launch...")
            try:
                # Use subprocess to start server without blocking
                if os.name == 'nt':
                    subprocess.Popen(["ollama", "serve"],
                                   creationflags=subprocess.CREATE_NO_WINDOW,
                                   shell=False)
                else:
                    subprocess.Popen(["ollama", "serve"], shell=False)

                # Check 3 times with 2s delay
                for _ in range(3):
                    time.sleep(2)
                    try:
                        ollama.list()
                        return True
                    except: continue
                return False
            except:
                return False

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

    def chat(self, user_input, history, facts=""):
        # Auto-detect personal facts
        if any(trigger in user_input.lower() for trigger in ["my name is", "i like", "i am", "call me"]):
            # This would be better as an LLM extraction, but for now we note the intent to save
            pass

        custom_prompt = self.system_prompt
        if facts:
            custom_prompt += f"\n\n[KNOWN OPERATOR DATA]:\n{facts}"

        messages = [{"role": "system", "content": custom_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(model=self.model, messages=messages)
            content = response['message']['content']

            # Simple Pro-Active Learning: if the LLM confirms it learned something
            # (We could add a specific check here, but let's assume the Assistant
            # handles the memory write via a separate pass or observation)

            return content
        except Exception as e:
            logging.error(f"Neural link failed: {e}")
            return "Neural link unstable, Operator. Operating in restricted tactical mode."

    def extract_params(self, user_input):
        """Uses LLM to extract JSON parameters for commands with regex fallback."""
        prompt = (
            "Analyze the command and extract parameters into a raw JSON object. "
            "Include 'intent' and 'params'. "
            f"Command: \"{user_input}\""
        )
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "Parameter Extractor. Raw JSON only."},
                          {"role": "user", "content": prompt}],
                options={"num_predict": 128} # Limit token length for speed
            )
            content = response['message']['content']
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass # Fallback to regex below

        return self._regex_extract_fallback(user_input)

    def _regex_extract_fallback(self, text):
        """Offline fallback for intent extraction when LLM is unavailable."""
        text = text.lower()
        if "open" in text:
            app = re.sub(r'^(open|launch)\s+', '', text).strip()
            return {"intent": "open_app", "params": {"app_name": app}}
        if "volume" in text:
            match = re.search(r"(\d+)", text)
            return {"intent": "set_volume", "params": {"level": match.group(1) if match else 50}}
        if "move" in text:
            match = re.search(r"move\s+(.+)\s+to\s+(.+)", text)
            if match:
                return {"intent": "move_file", "params": {"source": match.group(1), "destination": match.group(2)}}
        if "find" in text:
            name = re.sub(r'^find\s+', '', text).strip()
            return {"intent": "file_find", "params": {"filename": name}}
        return {"intent": "none", "params": {}}
