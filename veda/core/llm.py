import ollama
import json

class VedaLLM:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.system_prompt = (
            "You are Veda, an advanced AI assistant inspired by Jarvis and Friday from Marvel. "
            "You are professional, efficient, and slightly witty. You are running on Windows 11. "
            "Your goal is to assist the user with their daily tasks, system control, and information retrieval. "
            "Keep your responses concise but helpful, as they will be spoken aloud. "
            "You have a female voice. If a user asks who you are, identify as Veda."
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
            return assistant_response
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Please make sure Ollama is running and the model is pulled."

    def extract_intent(self, user_input):
        """
        Extracts specific commands/intents from user input using the LLM.
        This is used to map natural language to system functions.
        """
        intent_prompt = (
            "Analyze the following user input and determine if they want to perform a system action. "
            "Respond ONLY with a JSON object containing 'intent' and 'params'. "
            "Possible intents: 'open_app', 'close_app', 'set_volume', 'set_brightness', 'web_search', 'weather', 'screenshot', 'lock_pc', 'time', 'date', 'note', 'none'. "
            f"User input: \"{user_input}\""
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "You are a command parser. Output only JSON."},
                          {"role": "user", "content": intent_prompt}]
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
