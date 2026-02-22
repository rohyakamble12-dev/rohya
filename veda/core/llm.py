import ollama
import json
from veda.core.memory import VedaMemory

class VedaLLM:
    def __init__(self, model="qwen2.5:3b"):
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
        # 1. Manage History (Pruning to last 10 messages + System Prompt)
        if len(self.messages) > 11:
            self.messages = [self.messages[0]] + self.messages[-10:]

        # 2. Strategic Context Retrieval
        facts = self.memory.get_all_facts_summary()

        # Search for similar document chunks
        doc_context = ""
        query_embedding = self.embed_text(user_input)
        if query_embedding:
            similar = self.memory.search_similar_chunks(query_embedding)
            if similar:
                doc_context = "\n[Relevant Documents]: " + " ".join([t[:200] for s, t, sim in similar])

        # Knowledge Graph Injection (Search keywords from user input in KG)
        kg_context = ""
        words = user_input.split()
        for word in words:
            if len(word) > 4: # Only check significant words
                rel = self.memory.get_connected_intel(word)
                if "No strategic links" not in rel:
                    kg_context += f"\n[Neural Link]: {rel}"

        context_str = f" [System: {context_info}]" if context_info else ""
        proto_str = f" [Protocols: {protocols}]" if protocols else ""

        # Merge Context
        context_aware_input = f"{context_str}{proto_str}\n[Memory: {facts}]{doc_context}{kg_context}\nUser: {user_input}"

        self.messages.append({"role": "user", "content": context_aware_input})

        try:
            response = ollama.chat(
                model=self.model,
                messages=self.messages
            )
            assistant_response = response['message']['content']
            # Store cleaned response for voice
            self.messages.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            error_msg = f"I'm having trouble connecting to my brain (Ollama). Error: {str(e)}"
            print(error_msg)
            return "System alert: Local LLM connection failed. Please ensure Ollama is active and 'qwen2.5:3b' is installed."

    def extract_intent(self, user_input):
        """Extracts system commands with confidence scoring."""
        intent_prompt = (
            "You are a command parser for Veda. Convert user input into a JSON command. "
            "Include a 'confidence' field (0.0 to 1.0). "
            "If it's just a conversation (not a command), set intent to 'none' and provide a conversational response in 'response'. "
            "Respond ONLY with raw JSON.\n\n"
            "Examples:\n"
            "User: 'open chrome and find cats' -> {'intent': 'web_find', 'params': {'query': 'cats'}, 'confidence': 1.0}\n"
            "User: 'search google for space' -> {'intent': 'web_find', 'params': {'query': 'space'}, 'confidence': 1.0}\n"
            "User: 'find my work folder' -> {'intent': 'file_search', 'params': {'filename': 'work'}, 'confidence': 0.9}\n"
            "User: 'open my resume' -> {'intent': 'open_item', 'params': {'item_name': 'resume'}, 'confidence': 0.95}\n"
            "User: 'initiate meeting protocol' -> {'intent': 'mission_protocol', 'params': {'name': 'meeting'}, 'confidence': 1.0}\n"
            "User: 'run a security audit' -> {'intent': 'security_audit', 'params': {}, 'confidence': 1.0}\n"
            "User: 'volume 80' -> {'intent': 'set_volume', 'params': {'level': 80}, 'confidence': 1.0}\n"
            "User: 'hello' -> {'intent': 'none', 'params': {}, 'response': 'Hello sir, systems are ready.', 'confidence': 1.0}\n"
            "User: 'after action report' -> {'intent': 'daily_report', 'params': {}, 'confidence': 1.0}\n"
            "User: 'morning briefing' -> {'intent': 'morning_briefing', 'params': {}, 'confidence': 1.0}\n\n"
            "Supported intents: open_app, close_app, set_volume, set_brightness, web_search, weather, "
            "screenshot, lock_pc, sleep, mute_toggle, morning_briefing, wifi_scan, password_recovery, "
            "switch_persona, sys_clean, sys_duplicates, sys_thermals, "
            "time, date, note, stock_price, crypto_price, remember_fact, vision_analyze, motivation, "
            "deep_research, read_doc, sys_health, net_info, storage_info, media_control, play_music, "
            "file_search, open_item, move_item, copy_item, delete_item, convert_item, "
            "zip_item, unzip_item, find_duplicates, find_large_files, encrypt_item, decrypt_item, "
            "batch_rename, organize_dir, search_content, init_project, folder_intel, backup_item, "
            "sys_integrity, bulk_media_op, empty_trash, file_info, "
            "set_mode, translate, start_recording, stop_recording, "
            "play_macro, ingest_web, todo_add, todo_list, todo_complete, pomodoro, define_protocol, "
            "run_protocol, mission_protocol, security_audit, link_intel, get_connected, calculate, "
            "set_wallpaper, set_timer, set_alarm, send_email, daily_report, "
            "sight, read_screen, read_physical, iot_control, help, test_sound, web_find, none.\n\n"
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
