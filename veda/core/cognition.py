import json
import ollama
from veda.utils.logger import logger

class VedaPlanner:
    def __init__(self, assistant):
        self.assistant = assistant
        self.model = assistant.llm.model

    def generate_plan(self, user_input):
        """Generates a multi-step execution plan in JSON format."""
        # Get available tools from PluginManager
        available_tools = list(self.assistant.plugins.intent_map.keys())

        prompt = (
            "You are the Strategic Planner for Veda. Break down the user's request into a sequence of tool calls. "
            "Respond ONLY with a JSON list of steps.\n\n"
            f"Available tools: {available_tools}\n"
            "If a step requires information from a previous step, use the 'await' keyword in params.\n\n"
            "Example:\n"
            "User: 'Find my resume and email it to Tony'\n"
            "Plan: [\n"
            "  {'intent': 'file_search', 'params': {'filename': 'resume'}},\n"
            "  {'intent': 'send_email', 'params': {'recipient': 'Tony', 'subject': 'Resume', 'body': 'Attached is the resume you requested.', 'attachment': 'await'}}\n"
            "]\n\n"
            f"User Input: {user_input}"
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "You are Veda's Strategic Planner. Respond ONLY with raw JSON."},
                          {"role": "user", "content": prompt}],
                options={"temperature": 0}
            )
            content = response['message']['content']
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except Exception as e:
            logger.error(f"Planning failed: {e}")

        return []

class VedaReflector:
    def __init__(self, assistant):
        self.assistant = assistant
        self.model = assistant.llm.model

    def critique_plan(self, plan):
        """Evaluates a plan for safety and efficiency."""
        # For now, a simple pass. We can add complex logic later.
        if not plan: return False, "Empty plan."

        # Check for multiple destructive actions
        destructive_count = 0
        for step in plan:
            if step.get('intent') in ['delete_item', 'shred', 'sys_clean']:
                destructive_count += 1

        if destructive_count > 2:
            return False, "Plan contains multiple destructive actions. Please proceed with caution."

        return True, "Plan approved."

    def reflect_on_output(self, response):
        """Self-critique the assistant's response for tone and clarity."""
        # This can be used to refine the final message
        return response
