import ast
import operator as op
import math

class SafeMathEvaluator:
    # Supported operators
    operators = {
        ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.pow,
        ast.USub: op.neg, ast.UAdd: op.pos, ast.Mod: op.mod
    }

    # Supported functions
    functions = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'sqrt': math.sqrt, 'abs': abs, 'log': math.log,
        'exp': math.exp, 'pow': pow, 'pi': math.pi, 'e': math.e
    }

    def evaluate(self, expr):
        try:
            # Complexity Limit: Prevent CPU exhaustion via massive strings
            if len(expr) > 1000: raise ValueError("Tactical Complexity Alert: Expression too long.")

            # Handle constants like pi/e if they are just strings
            if expr in self.functions and not callable(self.functions[expr]):
                return self.functions[expr]

            node = ast.parse(expr, mode='eval').body
            # Reset recursion guard
            self._depth = 0
            return self._eval(node)
        except Exception as e:
            raise ValueError(f"Invalid math expression: {e}")

    def _eval(self, node):
        # Tactical Recursion Guard: Prevent stack exhaustion
        self._depth += 1
        if self._depth > 50:
            raise ValueError("Tactical Complexity Alert: Mathematical recursion depth exceeded.")

        # Unified constant handling for various Python versions
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, (ast.Num, ast.Str, ast.Bytes, ast.NameConstant)): # Legacy fallbacks
            return getattr(node, 'n', getattr(node, 's', getattr(node, 'value', None)))
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval(node.operand))
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in self.functions and callable(self.functions[func_name]):
                args = [self._eval(arg) for arg in node.args]
                return self.functions[func_name](*args)
            raise ValueError(f"Function {func_name} is not tactical.")
        elif isinstance(node, ast.Name):
            if node.id in self.functions:
                return self.functions[node.id]
            raise ValueError(f"Variable {node.id} is not tactical.")
        else:
            raise TypeError(f"Unsupported AST node: {type(node)}")

evaluator = SafeMathEvaluator()
