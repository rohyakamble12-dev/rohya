import json
import ollama
from veda.utils.logger import logger

class VedaPlanner:
    def __init__(self, assistant):
        self.assistant = assistant
        self.model = assistant.llm.model

    def generate_plan(self, user_input):
        """Generates a multi-step execution plan with validation."""
        available_tools = list(self.assistant.plugins.intent_map.keys())

        prompt = (
            "Break down user request into JSON list of tool calls.\n"
            f"Tools: {available_tools}\n"
            "Schema: [{'intent': str, 'params': dict}]\n"
            f"Input: {user_input}"
        )

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "system", "content": "You are Veda's Planner. Output RAW JSON list only."},
                          {"role": "user", "content": prompt}],
                options={"temperature": 0}
            )
            content = response['message']['content']
            plan = self._parse_json(content)
            return self._validate_plan(plan)
        except Exception as e:
            logger.error(f"Planning Error: {e}")
            return []

    def _parse_json(self, content):
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except: pass
        return []

    def _validate_plan(self, plan):
        """Ensures the plan follows the expected structure and intents exist."""
        if not isinstance(plan, list): return []
        valid_plan = []
        for step in plan:
            if isinstance(step, dict) and 'intent' in step:
                if step['intent'] in self.assistant.plugins.intent_map:
                    valid_plan.append(step)
        return valid_plan

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
