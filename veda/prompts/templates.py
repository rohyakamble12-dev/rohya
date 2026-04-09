def get_summarize_prompt(text):
    return f"Summarize the following text concisely:\n\n{text}"

def get_explain_code_prompt(code, language='Python'):
    return f"Explain the following {language} code step by step:\n\n{code}"
