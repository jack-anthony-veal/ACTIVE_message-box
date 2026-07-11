import unittest
from unittest.mock import MagicMock, patch
from scripts.app.StateNavigator import StateNavigator

class TestStateNavigator(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.navigator = StateNavigator(self.mock_app)

    def test_init(self):
        self.assertEqual(self.navigator.app, self.mock_app)
        self.assertIsNone(self.navigator.current_state)
        self.assertIsNone(self.navigator.previous_state)
        self.assertIsNone(self.navigator.second_state_prior)
        self.assertIsNone(self.navigator.next_state)
        self.assertFalse(self.navigator.running)

    def test_current_state_check(self):
        mock_state = MagicMock()
        self.navigator.current_state = mock_state
        self.assertEqual(self.navigator.current_state_check, mock_state)

    def test_push_state_initial(self):
        mock_state = MagicMock()
        self.navigator.push_state(mock_state)
        mock_state.enter_state.assert_called_once()
        self.assertEqual(self.navigator.current_state, mock_state)
        self.assertIsNone(self.navigator.previous_state) # previous state should still be None

    def test_push_state_with_current_state_running(self):
        mock_current_state = MagicMock()
        mock_current_state.running = True
        self.navigator.current_state = mock_current_state

        mock_new_state = MagicMock()
        self.navigator.push_state(mock_new_state)

        mock_current_state.exit_state.assert_called_once()
        mock_new_state.enter_state.assert_called_once()
        self.assertEqual(self.navigator.current_state, mock_new_state)

    def test_push_state_with_current_state_not_running(self):
        mock_current_state = MagicMock()
        mock_current_state.running = False
        self.navigator.current_state = mock_current_state

        mock_new_state = MagicMock()
        self.navigator.push_state(mock_new_state)

        mock_current_state.exit_state.assert_not_called() # Should not exit if not running
        mock_new_state.enter_state.assert_called_once()
        self.assertEqual(self.navigator.current_state, mock_new_state)

    def test_pop_state(self):
        mock_previous_state = MagicMock()
        mock_current_state = MagicMock()
        self.navigator.previous_state = mock_previous_state
        self.navigator.current_state = mock_current_state

        self.navigator.pop_state()

        mock_current_state.exit_state.assert_called_once()
        mock_previous_state.enter_state.assert_called_once()
        self.assertEqual(self.navigator.current_state, mock_previous_state)

    def test_pop_state_no_previous(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state
        self.navigator.previous_state = None # Ensure no previous state

        self.navigator.pop_state()

        mock_current_state.exit_state.assert_called_once()
        # If previous_state is None, current_state should remain the same after pop
        self.assertEqual(self.navigator.current_state, mock_current_state)
        # No enter_state call on a None object, so no assertion for previous_state.enter_state

    def test_replace_state(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state

        mock_new_state = MagicMock()
        self.navigator.replace_state(mock_new_state)

        mock_current_state.exit_state.assert_not_called() # replace_state should not call exit
        mock_new_state.enter_state.assert_called_once()
        self.assertEqual(self.navigator.current_state, mock_new_state)

    def test_handle_input(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state
        event = "some_event"
        event_type = "some_type"

        self.navigator.handle_input(event, event_type)
        mock_current_state.handle_input.assert_called_once_with(event, event_type)

    def test_update(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state
        self.navigator.update()
        mock_current_state.update.assert_called_once()

    def test_draw(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state
        self.navigator.draw()
        mock_current_state.draw.assert_called_once()

    def test_exit(self):
        mock_current_state = MagicMock()
        self.navigator.current_state = mock_current_state
        self.navigator.exit()
        mock_current_state.exit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
