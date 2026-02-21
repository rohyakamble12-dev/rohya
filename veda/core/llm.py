import ollama
import json
from veda.core.memory import VedaMemory

class VedaLLM:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.memory = VedaMemory()
        self.system_prompt = (
            "You are Veda, a sophisticated AI partner inspired by JARVIS and FRIDAY. "
            "Witty, loyal, and technically sharp. Operating on Windows 11. "
            "Refer to the user as 'Sir' or 'Boss'. "
            "Proactive: monitor system health and analyze documents. "
            "IMPORTANT: Concise responses. Plain text ONLY. No markdown (asterisks, hashtags) or emojis."
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, user_input, context_info=None, protocols=None):
        """Generates a response from the LLM based on user input and system context."""
        # Inject memory facts into the context before chatting
        facts = self.memory.get_all_facts_summary()

        # Search for similar document chunks if relevant
        doc_context = ""
        query_embedding = self.embed_text(user_input)
        if query_embedding:
            similar = self.memory.search_similar_chunks(query_embedding)
            if similar:
                doc_context = "\n[Relevant Document Segments]:\n" + "\n".join([f"Source: {s} - {t}" for s, t, sim in similar])

        context_str = f" [Current System Context: {context_info}]" if context_info else ""
        proto_str = f" [Active Protocols: {protocols}]" if protocols else ""

        context_aware_input = f"[Memory Context: {facts}]{doc_context}{context_str}{proto_str}\nUser: {user_input}"

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
            "You are a command parser for Veda. Convert user input into a JSON command. "
            "If it's just a conversation (not a command), set intent to 'none' and provide a conversational response in 'response'. "
            "Respond ONLY with raw JSON.\n\n"
            "Examples:\n"
            "User: 'open chrome and find cats' -> {'intent': 'web_find', 'params': {'query': 'cats'}}\n"
            "User: 'search google for space' -> {'intent': 'web_find', 'params': {'query': 'space'}}\n"
            "User: 'find my work folder' -> {'intent': 'file_search', 'params': {'filename': 'work'}}\n"
            "User: 'volume 80' -> {'intent': 'set_volume', 'params': {'level': 80}}\n"
            "User: 'hello' -> {'intent': 'none', 'params': {}, 'response': 'Hello sir, systems are ready.'}\n"
            "User: 'morning briefing' -> {'intent': 'morning_briefing', 'params': {}}\n\n"
            "Supported intents: open_app, close_app, set_volume, set_brightness, web_search, weather, "
            "screenshot, lock_pc, sleep, mute_toggle, morning_briefing, wifi_scan, password_recovery, "
            "switch_persona, sys_clean, sys_duplicates, sys_thermals, "
            "time, date, note, stock_price, crypto_price, remember_fact, vision_analyze, motivation, "
            "deep_research, read_doc, sys_health, net_info, storage_info, media_control, play_music, "
            "file_search, file_info, set_mode, translate, start_recording, stop_recording, play_macro, "
            "ingest_web, todo_add, todo_list, todo_complete, pomodoro, define_protocol, run_protocol, "
            "calculate, sight, iot_control, help, test_sound, web_find, none.\n\n"
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

    def set_persona(self, persona_name):
        """Updates the system prompt and persona of the LLM."""
        base_instruction = " IMPORTANT: Always provide responses in plain text. Do NOT use markdown symbols or emojis."
        if persona_name.lower() == "jarvis":
            self.system_prompt = (
                "You are JARVIS, the legendary AI assistant. You are sophisticated, British, "
                "and fiercely loyal. You refer to the user as 'Sir' and manage system "
                "protocols with clinical precision. Keep responses witty and professional."
            ) + base_instruction
        else:
            self.system_prompt = (
                "You are FRIDAY, a sharp and highly capable AI. You are Irish, efficient, "
                "and proactive. You refer to the user as 'Boss' or 'Sir' and focus on "
                "immediate results and system security."
            ) + base_instruction
        self.reset_history()

    def embed_text(self, text):
        """Generates an embedding for the given text using Ollama."""
        try:
            # Note: Not all models support embeddings, but llama3.2 usually does
            response = ollama.embeddings(model=self.model, prompt=text)
            return response['embedding']
        except Exception as e:
            # Fallback/Log
            return None

    def reset_history(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
