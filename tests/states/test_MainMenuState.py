import unittest
from unittest.mock import MagicMock, patch
from scripts.states.MainMenuState import MainMenuCycleState
from scripts.states.PresetMenu import PresetMenu # Import for type checking in tests
from config.config import MENU_OPTIONS, MENU_OPTS_INDEX, IF_MESSAGE_NONE_DISP, MENU_Y

class TestMainMenuCycleState(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_app.display = MagicMock()
        self.mock_app.message_api = MagicMock()
        self.mock_app.state_manager = MagicMock()
        self.mock_app.storage = MagicMock()

        # Patch time.ticks_ms and time.ticks_diff for predictable time-based tests
        patcher_ticks_ms = patch('scripts.states.MainMenuState.time.ticks_ms', return_value=1000)
        self.mock_ticks_ms = patcher_ticks_ms.start()
        self.addCleanup(patcher_ticks_ms.stop)

        patcher_ticks_diff = patch('scripts.states.MainMenuState.time.ticks_diff', return_value=0)
        self.mock_ticks_diff = patcher_ticks_diff.start()
        self.addCleanup(patcher_ticks_diff.stop)

        patcher_gc = patch('scripts.states.MainMenuState.gc')
        self.mock_gc = patcher_gc.start()
        self.addCleanup(patcher_gc.stop)

        self.main_menu_state = MainMenuCycleState(self.mock_app)

    def test_init(self):
        self.assertEqual(self.main_menu_state.app, self.mock_app)
        self.assertEqual(self.main_menu_state.options, MENU_OPTIONS)
        self.assertFalse(self.main_menu_state.running)
        self.assertEqual(self.main_menu_state.current_index, 0)
        self.assertFalse(self.main_menu_state.index_updated)
        self.assertIsNone(self.main_menu_state.input_event)
        self.assertFalse(self.main_menu_state.to_refresh)
        self.assertIsNone(self.main_menu_state.data_to_draw)
        # Check last_checks initialization (tuple of (str, int))
        self.assertEqual(len(self.main_menu_state.last_checks), 2)
        self.assertEqual(self.main_menu_state.last_checks[0][0], MENU_OPTS_INDEX[0][0])
        self.assertIsInstance(self.main_menu_state.last_checks[0][1], int)
        self.assertEqual(self.main_menu_state.last_checks[1][0], MENU_OPTIONS[1][0])
        self.assertIsInstance(self.main_menu_state.last_checks[1][1], int)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "Test Message"))
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_enter_state_success(self, mock_show_menu_bar, mock_message_data):
        self.main_menu_state.enter_state()
        self.mock_app.display.power_on.assert_called_once()
        mock_message_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("Test Message", y_axis=8, wrap=True)
        mock_show_menu_bar.assert_called_once()

    @patch.object(MainMenuCycleState, 'message_data', side_effect=Exception("API Error"))
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_enter_state_api_error(self, mock_show_menu_bar, mock_message_data):
        self.main_menu_state.enter_state()
        self.mock_app.display.power_on.assert_called_once()
        mock_message_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with(
            'ERROR: API Error\nLikely no internet connection\n', y_axis=8, wrap=True)
        mock_show_menu_bar.assert_called_once()

    @patch.object(MainMenuCycleState, 'message_data', return_value=(False, None))
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_enter_state_no_message(self, mock_show_menu_bar, mock_message_data):
        self.main_menu_state.enter_state()
        self.mock_app.display.power_on.assert_called_once()
        mock_message_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with(IF_MESSAGE_NONE_DISP, y_axis=8, wrap=True)
        mock_show_menu_bar.assert_called_once()

    def test_handle_input_none_event(self):
        self.main_menu_state.handle_input(None, 'button')
        self.mock_app.display.custom_message.assert_not_called()
        self.mock_app.state_manager.push_state.assert_not_called()
        self.assertIsNone(self.main_menu_state.input_event)

    @patch.object(MainMenuCycleState, 'move_selection')
    def test_handle_input_button_preset_menu(self, mock_move_selection):
        self.main_menu_state.current_index = 1  # Index for Preset Menu
        self.main_menu_state.handle_input('press', 'button')
        self.mock_app.display.custom_message.assert_called_with("loading...", x_axis=0, y_axis=8, wrap=False, fill_all=True)
        self.mock_app.state_manager.push_state.assert_called_once()
        args, kwargs = self.mock_app.state_manager.push_state.call_args
        self.assertIsInstance(args[0], PresetMenu)
        self.assertEqual(args[0].app, self.mock_app)
        mock_move_selection.assert_not_called()

    @patch.object(MainMenuCycleState, 'move_selection')
    def test_handle_input_dial_movement(self, mock_move_selection):
        self.main_menu_state.current_index = 0
        self.main_menu_state.handle_input(1, 'dial') # Simulate dial turn right
        self.mock_app.display.custom_message.assert_called_with("loading...", x_axis=0, y_axis=8, wrap=False, fill_all=True)
        self.assertEqual(self.main_menu_state.input_event, 1)
        mock_move_selection.assert_called_once_with(1)
        self.mock_app.state_manager.push_state.assert_not_called()

    @patch.object(MainMenuCycleState, 'refresh_clock', return_value=True)
    def test_update_refresh_needed(self, mock_refresh_clock):
        self.main_menu_state.current_index = 0
        self.main_menu_state.last_checks[0] = (MENU_OPTS_INDEX[0][0], 500) # last check at 500ms
        self.mock_ticks_ms.return_value = 1000 # current time 1000ms

        self.main_menu_state.update()

        mock_refresh_clock.assert_called_once()
        self.assertEqual(self.main_menu_state.last_checks[0][1], 1000) # last_check_ms updated
        self.assertTrue(self.main_menu_state.to_refresh)

    @patch.object(MainMenuCycleState, 'refresh_clock', return_value=False)
    def test_update_no_refresh_needed(self, mock_refresh_clock):
        self.main_menu_state.current_index = 0
        self.main_menu_state.last_checks[0] = (MENU_OPTS_INDEX[0][0], 900) # last check at 900ms
        self.mock_ticks_ms.return_value = 1000 # current time 1000ms

        self.main_menu_state.update()

        mock_refresh_clock.assert_called_once()
        self.assertEqual(self.main_menu_state.last_checks[0][1], 900) # last_check_ms not updated
        self.assertFalse(self.main_menu_state.to_refresh)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "New Message"))
    @patch.object(MainMenuCycleState, 'preset_data', return_value=(True, "New Preset"))
    @patch.object(MainMenuCycleState, 'settings_data', return_value="Settings Page")
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_draw_index_updated_message(self, mock_show_menu_bar, mock_settings_data, mock_preset_data, mock_message_data):
        self.main_menu_state.index_updated = True
        self.main_menu_state.current_index = 0 # Message index
        self.main_menu_state.draw()

        mock_message_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("New Message", y_axis=8, wrap=True, fill_all=True)
        mock_show_menu_bar.assert_called_once()
        self.assertFalse(self.main_menu_state.index_updated)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "New Message"))
    @patch.object(MainMenuCycleState, 'preset_data', return_value=(True, "New Preset"))
    @patch.object(MainMenuCycleState, 'settings_data', return_value="Settings Page")
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_draw_index_updated_preset(self, mock_show_menu_bar, mock_settings_data, mock_preset_data, mock_message_data):
        self.main_menu_state.index_updated = True
        self.main_menu_state.current_index = 1 # Preset index
        self.main_menu_state.draw()

        mock_preset_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("New Preset", y_axis=8, wrap=True, fill_all=True)
        mock_show_menu_bar.assert_called_once()
        self.assertFalse(self.main_menu_state.index_updated)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "New Message"))
    @patch.object(MainMenuCycleState, 'preset_data', return_value=(True, "New Preset"))
    @patch.object(MainMenuCycleState, 'settings_data', return_value="Settings Page")
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_draw_index_updated_settings(self, mock_show_menu_bar, mock_settings_data, mock_preset_data, mock_message_data):
        self.main_menu_state.index_updated = True
        self.main_menu_state.current_index = 2 # Settings index
        self.main_menu_state.draw()

        mock_settings_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("Settings Page", y_axis=8, wrap=True, fill_all=True)
        mock_show_menu_bar.assert_called_once()
        self.assertFalse(self.main_menu_state.index_updated)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "Refreshed Message"))
    @patch.object(MainMenuCycleState, 'preset_data', return_value=(True, "Refreshed Preset"))
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_draw_to_refresh_message(self, mock_show_menu_bar, mock_preset_data, mock_message_data):
        self.main_menu_state.to_refresh = True
        self.main_menu_state.current_index = 0 # Message index
        self.main_menu_state.draw()

        mock_message_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("Refreshed Message", y_axis=8, wrap=True, fill_all=True)
        mock_show_menu_bar.assert_called_once()
        self.assertFalse(self.main_menu_state.to_refresh)

    @patch.object(MainMenuCycleState, 'message_data', return_value=(True, "Refreshed Message"))
    @patch.object(MainMenuCycleState, 'preset_data', return_value=(True, "Refreshed Preset"))
    @patch.object(MainMenuCycleState, 'show_menu_bar')
    def test_draw_to_refresh_preset(self, mock_show_menu_bar, mock_preset_data, mock_message_data):
        self.main_menu_state.to_refresh = True
        self.main_menu_state.current_index = 1 # Preset index
        self.main_menu_state.draw()

        mock_preset_data.assert_called_once()
        self.mock_app.display.custom_message.assert_called_with("Refreshed Preset", y_axis=8, wrap=True, fill_all=True)
        mock_show_menu_bar.assert_called_once()
        self.assertFalse(self.main_menu_state.to_refresh)

    def test_draw_no_update_no_refresh(self):
        self.main_menu_state.index_updated = False
        self.main_menu_state.to_refresh = False
        self.main_menu_state.draw()
        self.mock_app.display.custom_message.assert_not_called()

    def test_exit_state(self):
        self.main_menu_state.running = True
        self.main_menu_state.current_index = 5 # arbitrary value
        self.main_menu_state.exit_state()
        self.assertFalse(self.main_menu_state.running)
        self.assertEqual(self.main_menu_state.current_index, 5) # Should retain its value
        self.mock_gc.collect.assert_called_once()

    @patch('scripts.states.MainMenuState.math.floor', side_effect=lambda x: int(x)) # Mock math.floor for predictable results
    def test_show_menu_bar(self, mock_floor):
        self.main_menu_state.current_index = 0 # "Message"
        self.main_menu_state.show_menu_bar()
        expected_text = ' > ' + MENU_OPTIONS[0]
        # (len(" > Message") + 1) * 8 = (9+1)*8 = 80
        # centre = 128 / 2 = 64
        # x_axis = 64 - floor(80/2) = 64 - 40 = 24
        self.mock_app.display.custom_message.assert_called_with(
            expected_text,
            x_axis=24, y_axis=MENU_Y,
            fill_start_line=MENU_Y, fill_x_axis=128, fill_y_axis=8,
            wrap=False
        )

    def test_move_selection_right(self):
        self.main_menu_state.current_index = 0
        self.main_menu_state.move_selection(1) # Move right
        self.assertEqual(self.main_menu_state.current_index, 1)
        self.assertTrue(self.main_menu_state.index_updated)

    def test_move_selection_left(self):
        self.main_menu_state.current_index = 1
        self.main_menu_state.move_selection(-1) # Move left
        self.assertEqual(self.main_menu_state.current_index, 0)
        self.assertTrue(self.main_menu_state.index_updated)

    def test_move_selection_wrap_around_right(self):
        self.main_menu_state.current_index = len(MENU_OPTIONS) - 1 # Last index
        self.main_menu_state.move_selection(1)
        self.assertEqual(self.main_menu_state.current_index, 0) # Should wrap to first

    def test_move_selection_wrap_around_left(self):
        self.main_menu_state.current_index = 0 # First index
        self.main_menu_state.move_selection(-1)
        self.assertEqual(self.main_menu_state.current_index, len(MENU_OPTIONS) - 1) # Should wrap to last

    def test_refresh_clock_true(self):
        self.mock_ticks_ms.return_value = 2000
        self.mock_ticks_diff.return_value = 1500 # Difference is 1500ms
        # ms_new_event_limit is not directly passed, but taken from last_checks[current_index][1]
        # Let's assume a limit of 1000ms for this test
        result = self.main_menu_state.refresh_clock(1000, 500) # last_check_ms=500, limit=1000
        self.assertTrue(result)
        self.mock_ticks_diff.assert_called_with(2000, 500)

    def test_refresh_clock_false(self):
        self.mock_ticks_ms.return_value = 2000
        self.mock_ticks_diff.return_value = 500 # Difference is 500ms
        result = self.main_menu_state.refresh_clock(1000, 1500) # last_check_ms=1500, limit=1000
        self.assertFalse(result)
        self.mock_ticks_diff.assert_called_with(2000, 1500)

    def test_message_data_new_message(self):
        self.mock_app.message_api.read_new_message.return_value = (True, {"message": "Hello"})
        has_new, data = self.main_menu_state.message_data()
        self.assertTrue(has_new)
        self.assertEqual(data, {"message": "Hello"})
        self.mock_app.message_api.read_new_message.assert_called_once()
        self.mock_app.storage.write_display_data.assert_called_once_with({"message": "Hello"})
        self.mock_app.storage.read_display_data.assert_not_called()

    def test_message_data_no_new_message_with_storage_data(self):
        self.mock_app.message_api.read_new_message.return_value = (False, None)
        self.mock_app.storage.read_display_data.return_value = {"message": "Stored Message"}
        has_new, data = self.main_menu_state.message_data()
        self.assertFalse(has_new)
        self.assertEqual(data, "Stored Message")
        self.mock_app.message_api.read_new_message.assert_called_once()
        self.mock_app.storage.read_display_data.assert_called_once()
        self.mock_app.storage.write_display_data.assert_not_called()

    def test_message_data_no_new_message_no_storage_data(self):
        self.mock_app.message_api.read_new_message.return_value = (False, None)
        self.mock_app.storage.read_display_data.return_value = {"message": None}
        has_new, data = self.main_menu_state.message_data()
        self.assertFalse(has_new)
        self.assertIsNone(data) # Should return None if storage also has None
        self.mock_app.message_api.read_new_message.assert_called_once()
        self.mock_app.storage.read_display_data.assert_called_once()
        self.mock_app.storage.write_display_data.assert_not_called()

    def test_preset_data_available(self):
        self.mock_app.message_api.load_presets.return_value = (True, ["P1", "P2"])
        available, data = self.main_menu_state.preset_data()
        self.assertTrue(available)
        self.assertEqual(data, ["P1", "P2"])
        self.mock_app.message_api.load_presets.assert_called_once()
        self.mock_app.storage.write_preset_data.assert_called_once_with(["P1", "P2"])

    def test_preset_data_not_available(self):
        self.mock_app.message_api.load_presets.return_value = (False, None)
        available, data = self.main_menu_state.preset_data()
        self.assertFalse(available)
        self.assertEqual(data, ['No new presets', 'available'])
        self.mock_app.message_api.load_presets.assert_called_once()
        self.mock_app.storage.write_preset_data.assert_called_once_with(['No new presets', 'available'])

    def test_settings_data(self):
        result = self.main_menu_state.settings_data()
        self.assertEqual(result, "No settings page created yet...")

if __name__ == '__main__':
    unittest.main()
