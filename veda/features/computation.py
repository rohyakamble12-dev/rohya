import os
import wolframalpha

class ComputationEngine:
    @staticmethod
    def calculate(query):
        """Uses WolframAlpha to compute math and conversions."""
        try:
            # Try to get App ID from environment variable
            app_id = os.environ.get("WOLFRAM_APP_ID")

            if not app_id:
                # Fallback to a basic Python eval if no key is provided
                # Only allowing very basic math chars for safety
                import re
                if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', query):
                    try:
                        result = eval(query)
                        return f"The result is {result}"
                    except Exception:
                        pass
                return "WolframAlpha App ID is missing. Please set WOLFRAM_APP_ID in your environment variables for advanced calculations."

            client = wolframalpha.Client(app_id)
            res = client.query(query)

            # Extract the answer from the result
            answer = next(res.results).text
            return f"According to my calculations: {answer}"
        except StopIteration:
            return "I couldn't find an answer to that calculation."
        except Exception as e:
            return f"Computation failed: {str(e)}"
