import math
from veda.features.base import VedaPlugin, PermissionTier

class CalculatorPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("calculate", self.calculate, PermissionTier.SAFE)

    def calculate(self, params):
        expr = params.get("expression", "")
        try:
            safe_dict = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
                'pi': math.pi, 'e': math.e, 'pow': pow
            }
            res = eval(expr.replace('^', '**'), {"__builtins__": None}, safe_dict)
            return f"Result: {res}"
        except Exception as e:
            return f"Calculation failure: {e}"
