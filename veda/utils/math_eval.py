import ast
import operator

class SafeMathEvaluator:
    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg
        }

    def evaluate(self, expression):
        try:
            node = ast.parse(expression, mode='eval').body
            return self._eval(node)
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    def _eval(self, node):
        if isinstance(node, ast.Num):  # Legacy Python
            return node.n
        elif isinstance(node, ast.Constant):  # Modern Python
            return node.value
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval(node.operand))
        else:
            raise TypeError(f"Unsupported mathematical operation: {type(node)}")
