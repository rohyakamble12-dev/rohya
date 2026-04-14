import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the current directory to sys.path so we can import veda
sys.path.append(os.getcwd())

from veda.features.system.apps import AppControlPlugin as SystemPlugin

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

        # Mock web plugin
        mock_web = MagicMock()
        mock_web.search.return_value = "Mock web intelligence data."
        self.assistant.plugins.get_plugin.return_value = mock_web

        res = self.plugin.open_app({"app_name": "unknown_app"})

        # Verify fallback message contains the reports header
        self.assertIn("My web intelligence reports", res)
        # Verify web search was triggered via plugin
        mock_web.search.assert_called()

if __name__ == "__main__":
    unittest.main()
