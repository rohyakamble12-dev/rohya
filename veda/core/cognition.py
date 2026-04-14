import json
import ollama
from veda.utils.logger import logger

class VedaPlanner:
    def __init__(self, assistant):
        self.assistant = assistant
        self.model = assistant.llm.primary_model

    def generate_plan(self, user_input):
        """Generates an advanced multi-step execution plan with decomposition."""
        # 1. Quick Check: Handle simple requests immediately
        intent_data = self.assistant.llm.extract_intent(user_input)

        # Guard: If intent is 'chat' or 'none', planning is redundant. Orchestrator handles this.
        if intent_data.get("intent") in ["chat", "none"]:
             return []

        if intent_data.get("confidence", 0) >= 0.8:
             return [{"step": 1, "intent": intent_data["intent"], "params": intent_data["params"], "critical": True}]

        available_tools = []
        for intent, data in self.assistant.plugins.intent_map.items():
            # data is (plugin_instance, method_name, tier)
            plugin_instance, method_name, tier = data
            # tier is an enum, we need to access intent metadata from the plugin
            metadata = plugin_instance.intents.get(intent, {})
            available_tools.append({
                "intent": intent,
                "risk": metadata.get("risk_level", "Low"),
                "params": metadata.get("input_schema", {})
            })

        # Refined Tactical Prompt: Smaller, clearer, fewer tokens
        prompt = (
            "Veda Strategic Planner. Your mission is to decompose the user INPUT into a sequence of JSON sub-tasks using only the provided TOOLS.\n"
            "Syntax requirements: Must be a list of objects like [{'step': 1, 'intent': 'name', 'params': {}, 'critical': true}].\n"
            "Dependencies: Use 'params': {'key': '$RESULT_{n}'} to refer to a previous step's output.\n"
            "Action over words: Output the plan as raw JSON. No markdown. No conversational filler. No suggestions. Direct tactical execution only.\n"
            f"AVAILABLE TOOLS: {json.dumps(available_tools)}\n"
            f"INPUT: {user_input}"
        )

        try:
            # Free-Source Strategic Planning: Local-Only execution
            content = self.assistant.llm.chat_completion(
                messages=[{"role": "system", "content": "Veda Strategic Planner."}, {"role": "user", "content": prompt}]
            )
            plan = self._parse_json(content or "")
            return self._validate_plan(plan)
        except Exception as e:
            logger.error(f"Advanced Planning Failure: {e}")
            return self._survival_plan(user_input)

    def _survival_plan(self, user_input):
        """Emergency single-step planning when LLM is offline."""
        intent_data = self.assistant.llm.extract_intent(user_input)
        if intent_data.get("intent") != "none":
            return [{"step": 1, "intent": intent_data["intent"], "params": intent_data["params"], "critical": True}]
        return []

    def _parse_json(self, content):
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except Exception as e: logger.warning(f"Tactical Silencing: {e}")
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
        self.model = assistant.llm.primary_model

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
