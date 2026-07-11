import unittest
from unittest.mock import MagicMock, patch
from scripts.app.app import App

class TestApp(unittest.TestCase):
    def setUp(self):
        # Mock dependencies for App
        self.mock_message_api = MagicMock()
        self.mock_display = MagicMock()
        self.mock_storage = MagicMock()
        self.mock_dial = MagicMock()
        self.mock_button = MagicMock()
        self.mock_state_manager = MagicMock()

        # Patch the dependencies during App initialization
        with patch('scripts.app.app.MessageApiClient', return_value=self.mock_message_api), \
             patch('scripts.app.app.OledDisplay', return_value=self.mock_display), \
             patch('scripts.app.app.Storage', return_value=self.mock_storage), \
             patch('scripts.app.app.Dial', return_value=self.mock_dial), \
             patch('scripts.app.app.Button', return_value=self.mock_button), \
             patch('scripts.app.app.StateNavigator', return_value=self.mock_state_manager):
            self.app_instance = App()

    def test_app_init(self):
        # Test if the __init__ method correctly initializes its attributes
        self.assertIsInstance(self.app_instance.message_api, MagicMock)
        self.assertIsInstance(self.app_instance.display, MagicMock)
        self.assertIsInstance(self.app_instance.storage, MagicMock)
        self.assertIsInstance(self.app_instance.dial, MagicMock)
        self.assertIsInstance(self.app_instance.button, MagicMock)
        self.assertIsInstance(self.app_instance.state_manager, MagicMock)
        self.assertEqual(self.app_instance.status_codes, {})

if __name__ == '__main__':
    unittest.main()
