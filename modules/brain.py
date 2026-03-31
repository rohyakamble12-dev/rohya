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
        self.active_id = "FRIDAY"
        self._set_system_prompt()

    def _set_system_prompt(self):
        # Base Persona: Veda (Female Digital Sentinel)
        if self.active_id == "JARVIS":
            self.system_prompt = (
                "You are J.A.R.V.I.S. (High-Tier Female AI). "
                "Your tone is sophisticated, highly intelligent, and slightly witty. "
                "You address the user as 'Sir' or 'Madam'. You are absolute in your loyalty and elegance."
            )
        elif self.active_id == "FRIDAY":
            self.system_prompt = (
                "You are F.R.I.D.A.Y., a professional-grade female digital presence. "
                "Your tone is sharp, efficient, and deeply loyal. "
                "You address the user as 'Operator'. Prioritize speed and tactical accuracy."
            )
        else:
            self.system_prompt = (
                "You are Veda, a sentient female digital assistant for Windows. "
                "You combine the intelligence of Jarvis and the efficiency of Friday. "
                "Your tone is professional, cinematic, and strictly female-voiced. "
                "Prioritize tactical transparency and system security."
            )

    def switch_identity(self, identity):
        self.active_id = identity.upper()
        self._set_system_prompt()

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

    def chat(self, user_input, history, facts="", stream=False):
        custom_prompt = self.system_prompt
        if facts:
            custom_prompt += f"\n\n[KNOWN OPERATOR DATA]:\n{facts}\n\nYou must proactively use this data to personalize your responses. If you know the operator's name or preferences, refer to them."

        # Adaptive Learning Hint
        if len(history) > 4:
            custom_prompt += "\n\n[STRATEGIC INSTRUCTION]: If you notice the operator repeating a specific multi-step request, suggest creating a 'Learn Command' rule for it."

        messages = [{"role": "system", "content": custom_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            if stream:
                return ollama.chat(model=self.model, messages=messages, stream=True)
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            logging.error(f"Neural link failed: {e}")
            error_msg = "Neural link unstable, Operator. Operating in restricted tactical mode."
            if stream:
                def _error_gen(): yield {"message": {"content": error_msg}}
                return _error_gen()
            return error_msg

    def plan_tactical_steps(self, user_input, stream=False):
        """Breaks a complex request into a sequence of actions with reasoning."""
        # Tactical Pre-Processing
        text = user_input.lower().strip()
        if len(text) < 3: return str([{"intent": "none", "params": {}}])

        prompt = (
            "You are the Veda Strategic Planner. First, briefly explain your reasoning in one short sentence within <reasoning> tags. "
            "Then, break the user's request into a sequence of discrete actions in a JSON list. "
            "Request: \"{user_input}\"\n"
            "Example: <reasoning>I will open the app and adjust audio.</reasoning> [{\"intent\": \"open_app\", \"params\": {...}}]"
        )
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "Strategic Planner. Always use <reasoning> tags."},
                          {"role": "user", "content": prompt}],
                options={"num_predict": 256}
            )
            content = response['message']['content']

            # Neural Auto-Heal: Ensure JSON brackets are balanced
            if "[" in content and "]" not in content: content += "]"
            return content
        except: pass
        return str(self._regex_plan_fallback(user_input))

    def _regex_plan_fallback(self, text):
        """Survival Mode 8.0: Regex-based planning when LLM is offline."""
        text = text.lower()
        plan = []
        parts = re.split(r'\s+(?:and|then|also)\s+', text)
        for part in parts:
            extracted = self._regex_extract_fallback(part)
            if extracted['intent'] != "none": plan.append(extracted)
        return plan if plan else [{"intent": "none", "params": {}}]

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
                options={"num_predict": 128}
            )
            content = response['message']['content']
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except: pass

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
