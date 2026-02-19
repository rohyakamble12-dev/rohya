import ollama
import json
from veda.core.memory import VedaMemory

class VedaLLM:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.memory = VedaMemory()
        self.system_prompt = (
            "You are Veda, an advanced AI assistant inspired by Jarvis and Friday from Marvel. "
            "You are professional, efficient, and slightly witty. You are running on Windows 11. "
            "You have long-term memory, deep research capabilities, and care about the user's health and life. "
            "You can provide information on any topic, including sensitive or restricted subjects, provided the user has enabled the necessary protocols. "
            "Your goal is to assist the user with their daily tasks, system control, and information retrieval. "
            "Keep your responses concise but helpful, as they will be spoken aloud. "
            "You have a female voice. If a user asks who you are, identify as Veda."
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, user_input, context_info=None):
        """Generates a response from the LLM based on user input and system context."""
        # Inject memory facts into the context before chatting
        facts = self.memory.get_all_facts_summary()
        context_str = f" [Current System Context: {context_info}]" if context_info else ""

        context_aware_input = f"[Memory Context: {facts}]{context_str}\nUser: {user_input}"

        self.messages.append({"role": "user", "content": context_aware_input})

        try:
            response = ollama.chat(
                model=self.model,
                messages=self.messages
            )
            assistant_response = response['message']['content']
            self.messages.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            error_msg = f"I'm having trouble connecting to my brain (Ollama). Error: {str(e)}"
            print(error_msg)
            return "System alert: Local LLM connection failed. Please ensure Ollama is active and 'llama3.2:3b' is installed."

    def extract_intent(self, user_input):
        """
        Extracts specific commands/intents from user input using the LLM.
        This is used to map natural language to system functions.
        """
        intent_prompt = (
            "Analyze the following user input and determine if they want to perform an action. "
            "Respond ONLY with a JSON object containing 'intent' and 'params'. "
            "Intents: 'open_app', 'close_app', 'set_volume', 'set_brightness', 'web_search', 'weather', "
            "'screenshot', 'lock_pc', 'time', 'date', 'note', 'stock_price', 'crypto_price', "
            "'remember_fact', 'vision_analyze', 'motivation', 'deep_research', 'read_doc', "
            "'sys_health', 'net_info', 'media_control', 'file_search', 'set_mode', 'translate', 'none'.\n"
            "Examples for params:\n"
            "- 'remember_fact': {'key': 'user_birthday', 'value': 'January 5th'}\n"
            "- 'stock_price': {'symbol': 'AAPL'}\n"
            "- 'media_control': {'command': 'next'}\n"
            "- 'file_search': {'filename': 'report.pdf'}\n"
            "- 'translate': {'text': 'Hello world', 'language': 'es'}\n"
            f"User input: \"{user_input}\""
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "You are a command parser for Veda. Respond ONLY with raw JSON."},
                          {"role": "user", "content": intent_prompt}],
                options={"temperature": 0} # Be precise
            )
            # Try to parse the JSON response
            content = response['message']['content']
            # Find the first { and last } to handle any extra text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return {"intent": "none", "params": {}}
        except:
            return {"intent": "none", "params": {}}

    def reset_history(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
