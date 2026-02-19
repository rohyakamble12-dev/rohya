try:
    print("Testing imports...")
    from veda.core.assistant import VedaAssistant
    print("VedaAssistant imported successfully.")

    from veda.ui.gui import VedaGUI
    print("VedaGUI imported successfully.")

    # Mocking GUI for Assistant initialization
    class MockGUI:
        def update_chat(self, sender, msg): pass
        def set_voice_active(self, active): pass
        def show_suggestion(self, tip): pass
        def after(self, ms, func, *args): pass
        def pulse_status(self): pass
        def update_metrics(self): pass
        def reset_voice_button(self): pass

    # We won't actually init because it might try to connect to Ollama or init Audio
    print("Import tests passed.")
except Exception as e:
    print(f"Import test failed: {e}")
    import traceback
    traceback.print_exc()
