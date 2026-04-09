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

    @patch('os.startfile')
    @patch('subprocess.Popen')
    @patch('webbrowser.open')
    def test_open_app_fallback(self, mock_web, mock_popen, mock_startfile):
        # Simulate app not found
        mock_startfile.side_effect = Exception("Not found")
        mock_popen.side_effect = Exception("Not found")

        res = self.plugin.open_app({"app_name": "unknown_app"})

        # Verify fallback message
        self.assertIn("Initiating web search sequence", res)
        # Verify web search was triggered
        mock_web.assert_called()

if __name__ == "__main__":
    unittest.main()
