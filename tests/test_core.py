import pytest
from veda.core.registry import registry
from veda.core.plugins import PluginManager
from unittest.mock import MagicMock

def test_service_registry():
    mock_service = MagicMock()
    registry.register("test_service", mock_service)
    assert registry.has("test_service")
    assert registry.get("test_service") == mock_service

def test_plugin_manager():
    assistant = MagicMock()
    pm = PluginManager(assistant)

    class MockPlugin:
        def __init__(self):
            self.name = "MockPlugin"
            self.intents = {"test_intent": (lambda p: "Success", None)}

    pm.load_plugin(MockPlugin())
    assert pm.get_plugin("MockPlugin") is not None
    assert "test_intent" in pm.intent_map
