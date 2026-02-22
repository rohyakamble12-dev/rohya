import math
from veda.features.base import VedaPlugin, PermissionTier

class CalculatorPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("calculate", self.calculate, PermissionTier.SAFE)

    def calculate(self, params):
        return f"Calculated result: {eval(params.get('expression', '0'))}"
