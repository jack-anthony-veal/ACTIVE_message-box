import unittest
from unittest.mock import MagicMock, patch, mock_open
from scripts.hardware_devices.storage import Storage
from config.config import DISPLAY_FILE, PRESET_FILE
import ujson

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.storage = Storage()

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    def test_call_success(self, mock_file_open):
        mock_file_open.return_value.read.return_value = "some data"
        success, error = self.storage()
        self.assertTrue(success)
        self.assertIsNone(error)
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "r")
        mock_file_open.return_value.read.assert_called_once()
        mock_file_open.return_value.close.assert_called_once()

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    def test_call_failure(self, mock_file_open):
        mock_file_open.side_effect = IOError("File not found")
        success, error = self.storage()
        self.assertFalse(success)
        self.assertIsInstance(error, IOError)
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "r")
        # close should not be called if open fails

    def test_ensure_dict_none(self):
        result = self.storage.ensure_dict(None)
        self.assertEqual(result, {"message": None})

    def test_ensure_dict_dict(self):
        data = {"key": "value"}
        result = self.storage.ensure_dict(data)
        self.assertEqual(result, data)

    def test_ensure_dict_bytes(self):
        data = b'{"key": "value"}'
        result = self.storage.ensure_dict(data)
        self.assertEqual(result, {"key": "value"})

    def test_ensure_dict_list_with_key(self):
        data = ["item1", "item2"]
        result = self.storage.ensure_dict(data, key="items")
        self.assertEqual(result, {"items": ["item1", "item2"]})

    def test_ensure_dict_list_without_key_raises_error(self):
        data = ["item1", "item2"]
        with self.assertRaises(TypeError): # The original code would proceed and likely fail later or return unexpected
            self.storage.ensure_dict(data) # Assuming it should raise an error or handle differently

    def test_ensure_dict_empty_string(self):
        result = self.storage.ensure_dict("")
        self.assertEqual(result, {"message": None})

    def test_ensure_dict_valid_json_string(self):
        data = '{"key": "value"}'
        result = self.storage.ensure_dict(data)
        self.assertEqual(result, {"key": "value"})

    def test_ensure_dict_invalid_json_string(self):
        data = 'not a json'
        result = self.storage.ensure_dict(data)
        self.assertEqual(result, {"message": "not a json"})

    def test_ensure_dict_plain_string(self):
        data = 'just a string'
        result = self.storage.ensure_dict(data)
        self.assertEqual(result, {"message": "just a string"})

    def test_ensure_dict_unsupported_type(self):
        with self.assertRaises(TypeError):
            self.storage.ensure_dict(123)

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open, read_data='{"message": "display data"}')
    @patch.object(Storage, 'ensure_dict', side_effect=lambda x, key=None: ujson.loads(x) if isinstance(x, str) else x)
    def test_read_display_data_success(self, mock_ensure_dict, mock_file_open):
        result = self.storage.read_display_data()
        self.assertEqual(result, {"message": "display data"})
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "r")
        mock_file_open.return_value.read.assert_called_once()
        mock_file_open.return_value.close.assert_called_once()
        mock_ensure_dict.assert_called_once_with('{"message": "display data"}')

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    @patch.object(Storage, 'ensure_dict')
    def test_read_display_data_file_error(self, mock_ensure_dict, mock_file_open):
        mock_file_open.side_effect = IOError("Read error")
        result = self.storage.read_display_data()
        self.assertEqual(result, {"message": None})
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "r")
        mock_ensure_dict.assert_not_called() # ensure_dict should not be called if file open fails

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open, read_data='{"presets": ["p1", "p2"]}')
    @patch.object(Storage, 'ensure_dict', side_effect=lambda x, key=None: ujson.loads(x) if isinstance(x, str) else x)
    def test_read_preset_data_success(self, mock_ensure_dict, mock_file_open):
        result = self.storage.read_preset_data()
        self.assertEqual(result, {"presets": ["p1", "p2"]})
        mock_file_open.assert_called_once_with(PRESET_FILE, "r")
        mock_file_open.return_value.read.assert_called_once()
        mock_file_open.return_value.close.assert_called_once()
        mock_ensure_dict.assert_called_once_with('{"presets": ["p1", "p2"]}')

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    @patch.object(Storage, 'ensure_dict')
    def test_read_preset_data_file_error(self, mock_ensure_dict, mock_file_open):
        mock_file_open.side_effect = IOError("Read error")
        result = self.storage.read_preset_data()
        self.assertEqual(result, {"message": None})
        mock_file_open.assert_called_once_with(PRESET_FILE, "r")
        mock_ensure_dict.assert_not_called()

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    @patch.object(Storage, 'ensure_dict', return_value={"presets": ["new_p1", "new_p2"]})
    @patch('scripts.hardware_devices.storage.ujson.dumps', return_value='{"presets": ["new_p1", "new_p2"]}')
    def test_write_preset_data(self, mock_dumps, mock_ensure_dict, mock_file_open):
        preset_data = ["new_p1", "new_p2"]
        result = self.storage.write_preset_data(preset_data)
        self.assertEqual(result, {"presets": ["new_p1", "new_p2"]})
        mock_ensure_dict.assert_called_once_with(preset_data, key="presets")
        mock_file_open.assert_called_once_with(PRESET_FILE, "w")
        mock_file_open.return_value.write.assert_called_once_with('{"presets": ["new_p1", "new_p2"]}')
        mock_file_open.return_value.close.assert_called_once()
        mock_dumps.assert_called_once_with({"presets": ["new_p1", "new_p2"]})

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    @patch.object(Storage, 'ensure_dict', return_value={"message": "new display msg"})
    @patch('scripts.hardware_devices.storage.ujson.dumps', return_value='{"message": "new display msg"}')
    def test_write_display_data_dict_input(self, mock_dumps, mock_ensure_dict, mock_file_open):
        display_data = {"message": "new display msg"}
        result = self.storage.write_display_data(display_data)
        self.assertEqual(result, {"message": "new display msg"})
        mock_ensure_dict.assert_called_once_with(display_data, key="message")
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "w")
        mock_file_open.return_value.write.assert_called_once_with('{"message": "new display msg"}')
        mock_file_open.return_value.close.assert_called_once()
        mock_dumps.assert_called_once_with({"message": "new display msg"})

    @patch('scripts.hardware_devices.storage.open', new_callable=mock_open)
    @patch.object(Storage, 'ensure_dict', return_value={"message": "simple string"})
    @patch('scripts.hardware_devices.storage.ujson.dumps', return_value='{"message": "simple string"}')
    def test_write_display_data_string_input(self, mock_dumps, mock_ensure_dict, mock_file_open):
        display_data = "simple string"
        result = self.storage.write_display_data(display_data)
        self.assertEqual(result, {"message": "simple string"})
        # The first call to ensure_dict is implicit in the method, then explicit
        # The method first converts string to dict, then passes to ensure_dict
        mock_ensure_dict.assert_called_once_with({"message": "simple string"}, key="message")
        mock_file_open.assert_called_once_with(DISPLAY_FILE, "w")
        mock_file_open.return_value.write.assert_called_once_with('{"message": "simple string"}')
        mock_file_open.return_value.close.assert_called_once()
        mock_dumps.assert_called_once_with({"message": "simple string"})

if __name__ == '__main__':
    unittest.main()
