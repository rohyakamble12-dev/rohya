import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the current directory to sys.path so we can import veda
sys.path.append(os.getcwd())

from veda.features.system_control import SystemPlugin

class TestSystemFallback(unittest.TestCase):
    def setUp(self):
        self.assistant = MagicMock()
        self.plugin = SystemPlugin(self.assistant)

    @patch('os.startfile', create=True)
    @patch('subprocess.Popen')
    def test_open_app_fallback(self, mock_popen, mock_startfile):
        # Simulate app not found
        mock_startfile.side_effect = Exception("Not found")
        mock_popen.side_effect = Exception("Not found")

        # Mock the WebPlugin to avoid actual network calls
        mock_web_plugin = MagicMock()
        mock_web_plugin.search.return_value = "Mock Intel"
        self.assistant.plugins.get_plugin.return_value = mock_web_plugin

        res = self.plugin.open_app({"app_name": "unknown_app"})

        # Verify fallback message
        self.assertIn("Initiating web search sequence", res)
        # Verify web search plugin was triggered
        mock_web_plugin.search.assert_called()

if __name__ == "__main__":
    unittest.main()
