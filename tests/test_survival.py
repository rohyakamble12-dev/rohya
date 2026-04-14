import pytest
from veda.core.llm import VedaLLM

def test_survival_fallback():
    # Test with a mock that forces failure or just test the logic
    llm = VedaLLM()
    # Survival Chat
    res = llm._survival_chat("hello")
    assert "survival mode" in res.lower()

    # Survival Intent
    intent = llm._survival_intent_extraction("open chrome")
    assert intent["intent"] == "open_app"
    assert intent["params"]["app_name"] == "chrome"
    assert intent["survival"] == True
    print("Survival Mode Test: PASSED")

if __name__ == "__main__":
    test_survival_fallback()
