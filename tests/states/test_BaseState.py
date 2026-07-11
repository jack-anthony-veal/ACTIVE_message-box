import unittest
from unittest.mock import MagicMock
from scripts.states.BaseState import BaseState

class TestBaseState(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.base_state = BaseState(self.mock_app)

    def test_init(self):
        self.assertEqual(self.base_state.app, self.mock_app)

    def test_enter_state(self):
        # Since it's a placeholder, we just check if it can be called without error
        try:
            self.base_state.enter_state()
        except Exception as e:
            self.fail(f"enter_state raised an unexpected exception: {e}")

    def test_exit_state(self):
        # Since it's a placeholder, we just check if it can be called without error
        try:
            self.base_state.exit_state()
        except Exception as e:
            self.fail(f"exit_state raised an unexpected exception: {e}")

    def test_handle_input(self):
        # Since it's a placeholder, we just check if it can be called without error
        try:
            self.base_state.handle_input()
        except Exception as e:
            self.fail(f"handle_input raised an unexpected exception: {e}")

    def test_update_each_frame(self):
        # Since it's a placeholder, we just check if it can be called without error
        try:
            self.base_state.update_each_frame()
        except Exception as e:
            self.fail(f"update_each_frame raised an unexpected exception: {e}")

    def test_draw(self):
        # Since it's a placeholder, we just check if it can be called without error
        try:
            self.base_state.draw()
        except Exception as e:
            self.fail(f"draw raised an unexpected exception: {e}")

if __name__ == '__main__':
    unittest.main()
