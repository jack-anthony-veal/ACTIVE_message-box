import unittest
from unittest.mock import MagicMock, patch
from scripts.app.api import MessageApiClient

class TestMessageApiClient(unittest.TestCase):
    def setUp(self):
        # Patch external dependencies for MessageApiClient
        self.patcher_requests = patch('scripts.app.api.requests')
        self.mock_requests = self.patcher_requests.start()
        self.patcher_gc = patch('scripts.app.api.gc')
        self.mock_gc = self.patcher_gc.start()

        self.api_client = MessageApiClient()

    def tearDown(self):
        self.patcher_requests.stop()
        self.patcher_gc.stop()

    def test_init(self):
        self.assertEqual(self.api_client.read_path, "/read/")
        self.assertEqual(self.api_client.send_path, "/send/")
        self.assertIsNotNone(self.api_client.server_url)
        self.assertIsNotNone(self.api_client.api_token)
        self.assertIn("content-type", self.api_client.headers)
        self.assertIn("box-token", self.api_client.headers)
        self.assertIn("Connection", self.api_client.headers)

    @patch('scripts.app.api.requests.get')
    def test_get_json_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_response.text = '{"key": "value"}'
        mock_get.return_value.__enter__.return_value = mock_response

        url = "http://test.com/api"
        result = self.api_client.get_json(url)

        mock_get.assert_called_once_with(url, headers=self.api_client.headers, timeout=5)
        self.assertEqual(result, {"key": "value"})
        self.mock_gc.collect.assert_called()

    @patch('scripts.app.api.requests.get')
    def test_get_json_http_error(self, mock_get):
        mock_get.side_effect = Exception("HTTP Error")

        url = "http://test.com/api"
        result = self.api_client.get_json(url)

        mock_get.assert_called_once_with(url, headers=self.api_client.headers, timeout=5)
        self.assertIsNone(result)
        self.mock_gc.collect.assert_called()

    @patch('scripts.app.api.requests.get')
    def test_get_json_parse_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("JSON Parse Error")
        mock_response.text = "Not JSON"
        mock_get.return_value.__enter__.return_value = mock_response

        url = "http://test.com/api"
        result = self.api_client.get_json(url)

        mock_get.assert_called_once_with(url, headers=self.api_client.headers, timeout=5)
        self.assertEqual(result, "Not JSON") # Expecting raw text on JSON parse error
        self.mock_gc.collect.assert_called()

    @patch.object(MessageApiClient, 'get_json')
    def test_load_presets_success(self, mock_get_json):
        mock_get_json.return_value = {"presets": ["preset1", "preset2"]}
        success, presets = self.api_client.load_presets()
        self.assertTrue(success)
        self.assertEqual(presets, ["preset1", "preset2"])
        mock_get_json.assert_called_once()

    @patch.object(MessageApiClient, 'get_json')
    def test_load_presets_no_data(self, mock_get_json):
        mock_get_json.return_value = None
        success, presets = self.api_client.load_presets()
        self.assertFalse(success)
        self.assertEqual(presets, ["No presets", "Upload on site"])
        mock_get_json.assert_called_once()

    @patch.object(MessageApiClient, 'get_json')
    def test_read_new_message_success(self, mock_get_json):
        mock_get_json.return_value = {"message": "Hello", "sender": "Test"}
        success, message_data = self.api_client.read_new_message()
        self.assertTrue(success)
        self.assertEqual(message_data, {"message": "Hello", "sender": "Test"})
        mock_get_json.assert_called_once()

    @patch.object(MessageApiClient, 'get_json')
    def test_read_new_message_no_message(self, mock_get_json):
        mock_get_json.return_value = {"message": None}
        success, message_data = self.api_client.read_new_message()
        self.assertFalse(success)
        self.assertEqual(message_data, {"message": None})
        mock_get_json.assert_called_once()

    @patch.object(MessageApiClient, 'get_json')
    def test_read_new_message_no_data(self, mock_get_json):
        mock_get_json.return_value = None
        success, message_data = self.api_client.read_new_message()
        self.assertFalse(success)
        self.assertEqual(message_data, {"message": None})
        mock_get_json.assert_called_once()

    def test_send_preset(self):
        # This method is not implemented in the provided code, so we'll just test its existence
        # If it were implemented, we'd mock its dependencies and test its behavior
        with self.assertRaises(NotImplementedError): # Assuming it would raise this if not implemented
            self.api_client.send_preset(1)

if __name__ == '__main__':
    unittest.main()
