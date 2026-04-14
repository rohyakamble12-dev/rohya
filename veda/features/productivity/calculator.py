import math
import re
from veda.features.base import VedaPlugin, PermissionTier

class CalculatorPlugin(VedaPlugin):
    def setup(self):
        schema = {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "maxLength": 200}
            },
            "required": ["expression"],
            "additionalProperties": False
        }
        self.register_intent("calculate", self.calculate, PermissionTier.SAFE, input_schema=schema)

    def calculate(self, params):
        from veda.utils.safemath import evaluator
        expr = str(params.get('expression', '0'))

        try:
            # Absolute Zero-Trust: AST-based evaluation with no eval()
            result = evaluator.evaluate(expr)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation Error: {e}"
