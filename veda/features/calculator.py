import math

class VedaCalculator:
    @staticmethod
    def calculate(expression):
        """Safely evaluates a mathematical expression."""
        try:
            # Allow only a subset of safe math functions
            safe_dict = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
                'pi': math.pi, 'e': math.e, 'pow': pow
            }
            # Clean the expression
            expression = expression.replace('^', '**')
            result = eval(expression, {"__builtins__": None}, safe_dict)
            return f"The result is {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"

    @staticmethod
    def convert_units(value, from_unit, to_unit):
        """Simple unit conversion logic (extendable)."""
        conversions = {
            ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
            ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
            ('meters', 'feet'): lambda x: x * 3.28084,
            ('feet', 'meters'): lambda x: x / 3.28084,
            ('kilograms', 'pounds'): lambda x: x * 2.20462,
            ('pounds', 'kilograms'): lambda x: x / 2.20462
        }

        pair = (from_unit.lower(), to_unit.lower())
        if pair in conversions:
            result = conversions[pair](value)
            return f"{value} {from_unit} is equal to {round(result, 2)} {to_unit}."
        return "I don't have that conversion protocol in my database yet."
