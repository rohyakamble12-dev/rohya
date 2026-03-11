from veda.utils.math_eval import SafeMathEvaluator

class MathPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.evaluator = SafeMathEvaluator()

    def register_intents(self):
        return {
            "calculate": self.calculate
        }

    def calculate(self, params):
        expr = params.get("expression")
        if not expr: return "Intelligence missing for calculation."

        result = self.evaluator.evaluate(expr)
        return f"Calculation complete: {expr} = {result}"
