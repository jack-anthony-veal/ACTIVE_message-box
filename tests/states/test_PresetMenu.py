import unittest
from unittest.mock import MagicMock, patch
from scripts.states.PresetMenu import PresetMenu

class TestPresetMenu(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_app.display = MagicMock()
        self.mock_app.message_api = MagicMock()
        self.mock_app.state_manager = MagicMock()
        self.preset_menu = PresetMenu(self.mock_app)

    def test_init(self):
        self.assertEqual(self.preset_menu.app, self.mock_app)
        self.assertEqual(self.preset_menu.current_index_preset, 0)
        self.assertFalse(self.preset_menu.index_switched_preset)
        self.assertIsNone(self.preset_menu.preset_data_full)
        self.assertIsNone(self.preset_menu.preset_data_select)
        self.assertFalse(self.preset_menu.running)

    def test_exit_state(self):
        # exit_state is a placeholder, so just check if it runs without error
        try:
            self.preset_menu.exit_state()
        except Exception as e:
            self.fail(f"exit_state raised an unexpected exception: {e}")

    @patch('scripts.states.PresetMenu.time')
    def test_draw_index_switched(self, mock_time):
        self.preset_menu.index_switched_preset = True
        self.preset_menu.preset_data_full = ["Preset 1", "Preset 2"]
        self.preset_menu.current_index_preset = 0
        self.preset_menu.preset_body = MagicMock() # Mock preset_body to avoid its internal logic
        self.preset_menu.preset_header = MagicMock(return_value="HEADER")

        self.preset_menu.draw()

        self.assertEqual(self.preset_menu.preset_data_select, "Preset 1")
        mock_time.sleep_ms.assert_called() # Called twice for preset_body and custom_message
        self.preset_menu.preset_body.assert_called_once()
        self.mock_app.display.custom_message.assert_any_call("HEADER", x_axis=0, y_axis=0, fill_all=True, wrap=False)
        self.mock_app.display.custom_message.assert_any_call(self.preset_menu.preset_data_select, x_axis=0, y_axis=8, wrap=True, fill_all=False)
        self.assertFalse(self.preset_menu.index_switched_preset)

    def test_draw_index_not_switched(self):
        self.preset_menu.index_switched_preset = False
        self.preset_menu.draw()
        self.mock_app.display.custom_message.assert_not_called()

    def test_handle_input_button_event(self):
        self.preset_menu.handle_input('some_event', 'button')
        # No specific action defined for button event, so no assertions on state change
        # Just ensure it doesn't raise an error

    def test_handle_input_dial_event_positive(self):
        self.preset_menu.preset_data_full = ["P1", "P2", "P3"]
        self.preset_menu.current_index_preset = 0
        self.preset_menu.handle_input(1, 'dial') # event=1 for increment
        self.assertEqual(self.preset_menu.current_index_preset, 1)
        self.assertTrue(self.preset_menu.index_switched_preset)

    def test_handle_input_dial_event_negative(self):
        self.preset_menu.preset_data_full = ["P1", "P2", "P3"]
        self.preset_menu.current_index_preset = 1
        self.preset_menu.handle_input(-1, 'dial') # event=-1 for decrement
        self.assertEqual(self.preset_menu.current_index_preset, 0)
        self.assertTrue(self.preset_menu.index_switched_preset)

    def test_handle_input_dial_event_wrap_around(self):
        self.preset_menu.preset_data_full = ["P1", "P2", "P3"]
        self.preset_menu.current_index_preset = 2
        self.preset_menu.handle_input(1, 'dial') # Increment from last
        self.assertEqual(self.preset_menu.current_index_preset, 0)

        self.preset_menu.current_index_preset = 0
        self.preset_menu.handle_input(-1, 'dial') # Decrement from first
        self.assertEqual(self.preset_menu.current_index_preset, 2)

    def test_enter_state_success(self):
        self.mock_app.message_api.load_presets.return_value = (True, ["Preset A", "Preset B"])
        self.preset_menu.enter_state()

        self.assertEqual(self.mock_app.state_manager.current_state, self.preset_menu)
        self.mock_app.display.custom_message.assert_called_with("Loading...", x_axis=0, y_axis=8, fill_all=True, wrap=False)
        self.mock_app.message_api.load_presets.assert_called_once()
        self.assertEqual(self.preset_menu.preset_data_full, ["Preset A", "Preset B"])
        self.assertEqual(self.preset_menu.preset_data_select, "Preset A")
        self.assertTrue(self.preset_menu.index_switched_preset)

    def test_enter_state_no_presets(self):
        self.mock_app.message_api.load_presets.return_value = (False, ["No presets", "Upload on site"])
        self.preset_menu.enter_state()

        self.assertEqual(self.preset_menu.preset_data_full, ["No presets", "Upload on site"])
        self.assertEqual(self.preset_menu.preset_data_select, "No presets") # First element of the list
        self.assertTrue(self.preset_menu.index_switched_preset)

    def test_update(self):
        # update is a placeholder, so just check if it runs without error
        try:
            self.preset_menu.update()
        except Exception as e:
            self.fail(f"update raised an unexpected exception: {e}")

    def test_preset_header_short_data(self):
        self.preset_menu.preset_data_full = ["Short Data"]
        self.preset_menu.current_index_preset = 0
        header = self.preset_menu.preset_header()
        # Expected: PRESET1/Short Data... (16 chars total for data part)
        # 16 - len("PRESET1/") - len("...") = 16 - 8 - 3 = 5
        # So "Short" should be displayed
        self.assertEqual(header, "PRESET1/Short...")

    def test_preset_header_long_data(self):
        self.preset_menu.preset_data_full = ["This is a very long preset message that should be truncated"]
        self.preset_menu.current_index_preset = 0
        header = self.preset_menu.preset_header()
        # Expected: PRESET1/This ... (16 chars total)
        self.assertEqual(header, "PRESET1/This ...")

    def test_preset_header_list_data(self):
        # The original code has a list comprehension that doesn't modify header_data
        # due to a type check issue: `type(header_data == list)`.
        self.preset_menu.preset_data_full = ["List Item 1", "List Item 2"]
        self.preset_menu.current_index_preset = 0
        header = self.preset_menu.preset_header()
        # Expected: PRESET1/List ... (16 chars total)
        self.assertEqual(header, "PRESET1/List ...")

    def test_preset_body(self):
        self.preset_menu.preset_data_select = "This is a message longer than sixteen characters"
        self.preset_menu.preset_body()
        expected_lines = [
            "This is a messag",
            "e longer than si",
            "xteen characters"
        ]
        self.assertEqual(self.preset_menu.preset_data_select, expected_lines)

    def test_preset_body_short_message(self):
        self.preset_menu.preset_data_select = "Short message"
        self.preset_menu.preset_body()
        self.assertEqual(self.preset_menu.preset_data_select, ["Short message"])

if __name__ == '__main__':
    unittest.main()
