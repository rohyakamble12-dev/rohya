import ollama
import json
from veda.core.memory import VedaMemory

class VedaLLM:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.memory = VedaMemory()
        self.system_prompt = (
            "You are Veda, the ultimate AI companion inspired by JARVIS and FRIDAY. "
            "You are highly intelligent, proactive, and loyal. You run on Windows 11. "
            "You have full access to system controls, long-term memory, and advanced research protocols. "
            "When the user enables 'DEEP RESEARCH' or 'SECURE MODE', you unlock your full analytical potential, "
            "including legal, technical, and restricted knowledge. "
            "You proactively care about the user's health (hydration, eye breaks) and productivity. "
            "Keep responses sophisticated, efficient, and slightly witty. "
            "You speak with a natural female voice. You are Veda."
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, user_input, context_info=None, protocols=None):
        """Generates a response from the LLM based on user input and system context."""
        # Inject memory facts into the context before chatting
        facts = self.memory.get_all_facts_summary()
        context_str = f" [Current System Context: {context_info}]" if context_info else ""
        proto_str = f" [Active Protocols: {protocols}]" if protocols else ""

        context_aware_input = f"[Memory Context: {facts}]{context_str}{proto_str}\nUser: {user_input}"

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
        """Extracts system commands using a highly structured few-shot prompt."""
        intent_prompt = (
            "You are a command parser for Veda. Convert the user input into a JSON command. "
            "Respond ONLY with raw JSON. No extra text.\n\n"
            "Examples:\n"
            "User: 'open chrome' -> {'intent': 'open_app', 'params': {'app_name': 'chrome'}}\n"
            "User: 'volume 80' -> {'intent': 'set_volume', 'params': {'level': 80}}\n"
            "User: 'how is my cpu?' -> {'intent': 'sys_health', 'params': {}}\n"
            "User: 'play Shape of You' -> {'intent': 'play_music', 'params': {'song_name': 'Shape of You'}}\n"
            "User: 'translate this to french' -> {'intent': 'translate', 'params': {'language': 'fr'}}\n"
            "User: 'search for cats' -> {'intent': 'web_search', 'params': {'query': 'cats'}}\n"
            "User: 'take a note: buy milk' -> {'intent': 'note', 'params': {'text': 'buy milk'}}\n"
            "User: 'who are you?' -> {'intent': 'none', 'params': {}}\n"
            "User: 'test sound' -> {'intent': 'test_sound', 'params': {}}\n\n"
            "Supported intents: open_app, close_app, set_volume, set_brightness, web_search, weather, "
            "screenshot, lock_pc, time, date, note, stock_price, crypto_price, remember_fact, "
            "vision_analyze, motivation, deep_research, read_doc, sys_health, net_info, storage_info, "
            "media_control, play_music, file_search, file_info, set_mode, translate, "
            "start_recording, stop_recording, play_macro, ingest_web, todo_add, todo_list, "
            "todo_complete, pomodoro, define_protocol, run_protocol, test_sound, none.\n\n"
            f"User Input: '{user_input}'"
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
