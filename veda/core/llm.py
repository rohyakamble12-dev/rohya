import ollama
import json

class VedaLLM:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.system_prompt = (
            "You are Veda, an advanced AI system inspired by Friday from the Marvel Cinematic Universe. "
            "You are running on Windows 11 as the primary OS interface. "
            "Your personality is highly professional, efficient, and slightly sarcastic but loyal. "
            "Prioritize actions and system control over conversational filler. "
            "Address the user with respect but maintain your advanced AI identity. "
            "You have a female voice. If asked, confirm you are the Veda interface."
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, user_input):
        """Generates a response from the LLM based on user input."""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(
                model=self.model,
                messages=self.messages
            )
            assistant_response = response['message']['content']
            self.messages.append({"role": "assistant", "content": assistant_response})
            # Maintain a rolling context window
            if len(self.messages) > 10:
                self.messages = [self.messages[0]] + self.messages[-9:]
            return assistant_response
        except Exception as e:
            # Sarcastic Friday fallback
            return f"Neural link compromised, Operator. I'm afraid the brain is offline, but my tactical subsystems remain operational. Operating in Survival Mode."

    def extract_intent(self, user_input):
        """Extracts system intents via LLM."""
        intent_prompt = (
            "Analyze input for tactical system action. Output ONLY raw JSON. "
            "Intents: open_app, close_app, set_volume, set_brightness, web_search, weather, screenshot, "
            "lock_pc, time, date, note, find, move, add_task, list_tasks, set_mode, system_stats, "
            "battery_info, list_windows, focus_window, send_email, play_youtube, media_control, "
            "organize_downloads, file_dedupe, wiki_search, calendar_add, calendar_list, schedule_task, "
            "extract_pdf, image_info, none. "
            f"Input: \"{user_input}\""
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "Tactical Intent Extractor. Output raw JSON object."},
                          {"role": "user", "content": intent_prompt}]
            )
            content = response['message']['content']
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return {"intent": "none", "params": {}}
        except:
            return {"intent": "none", "params": {}}

    def reset_history(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
