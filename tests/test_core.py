import pytest
from veda.core.registry import registry
from veda.core.plugins import PluginManager
from veda.features.base import PermissionTier
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
            # Updated to match the refined Plugin structure
            def mock_method(p): return "Success"
            self.intents = {
                "test_intent": {
                    "method": mock_method,
                    "tier": PermissionTier.SAFE
                }
            }

    pm.load_plugin(MockPlugin())
    assert pm.get_plugin("MockPlugin") is not None
    assert "test_intent" in pm.intent_map
