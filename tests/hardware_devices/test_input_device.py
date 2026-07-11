import unittest
from unittest.mock import MagicMock, patch
from scripts.hardware_devices.input_device import ToggleInput, Dial, Button
from scripts.hardware_devices.input_device import RotaryIRQ # Import for patching
from machine import Pin # Import for patching
from config.config import INPUT_DEBOUNCE_MS

class TestToggleInput(unittest.TestCase):
    @patch('scripts.hardware_devices.input_device.RotaryIRQ')
    @patch('scripts.hardware_devices.input_device.Pin')
    def test_init(self, MockPin, MockRotaryIRQ):
        toggle_input = ToggleInput()
        MockRotaryIRQ.assert_called_once_with(
            pin_num_clk=25,
            pin_num_dt=26,
            incr=1,
            range_mode=RotaryIRQ.RANGE_UNBOUNDED,
            pull_up=True,
            half_step=False,
            reverse=True,
        )
        MockPin.assert_called_once_with(27, Pin.IN, Pin.PULL_UP)
        self.assertEqual(toggle_input.rotary_encoder, MockRotaryIRQ.return_value)
        self.assertEqual(toggle_input.button_pin, MockPin.return_value)

class TestDial(unittest.TestCase):
    def setUp(self):
        # Patch ToggleInput's __init__ to avoid actual hardware initialization
        with patch('scripts.hardware_devices.input_device.ToggleInput.__init__', return_value=None):
            self.dial = Dial()
            self.dial.rotary_encoder = MagicMock() # Manually set mock rotary_encoder
            self.dial.button_pin = MagicMock() # Manually set mock button_pin

        # Patch time functions
        self.patcher_ticks_ms = patch('scripts.hardware_devices.input_device.time.ticks_ms', return_value=1000)
        self.mock_ticks_ms = self.patcher_ticks_ms.start()
        self.addCleanup(self.patcher_ticks_ms.stop)

        self.patcher_ticks_diff = patch('scripts.hardware_devices.input_device.time.ticks_diff', return_value=0)
        self.mock_ticks_diff = self.patcher_ticks_diff.start()
        self.addCleanup(self.patcher_ticks_diff.stop)

        # Initialize Dial specific attributes
        self.dial.last_rotary_ms = 1000
        self.dial.last_value_call = 0
        self.dial.minimum_turn = 12

    def test_init(self):
        # Test that Dial's __init__ sets its specific attributes
        # ToggleInput.__init__ is mocked in setUp, so we only check Dial's own attributes
        self.assertEqual(self.dial.last_rotary_ms, 1000)
        self.assertEqual(self.dial.last_value_call, 0)
        self.assertEqual(self.dial.minimum_turn, 12)

    def test_event_type_property(self):
        self.assertEqual(self.dial.event_type, "dial")

    def test_value_property(self):
        self.dial.rotary_encoder.value.return_value = 5
        self.assertEqual(self.dial.value, 5)
        self.dial.rotary_encoder.value.assert_called_once()

    @patch.object(Dial, 'event_check', return_value=True)
    def test_event_property(self, mock_event_check):
        self.assertTrue(self.dial.event)
        mock_event_check.assert_called_once()

    def test_event_direction_positive(self):
        self.assertEqual(self.dial.event_direction(10), 1)

    def test_event_direction_negative(self):
        self.assertEqual(self.dial.event_direction(-5), -1)

    def test_value_different_no_change(self):
        self.dial.rotary_encoder.value.return_value = 0
        self.dial.last_value_call = 0
        self.assertFalse(self.dial.value_different())
        self.assertEqual(self.dial.last_value_call, 0)

    def test_value_different_change(self):
        self.dial.rotary_encoder.value.return_value = 5
        self.dial.last_value_call = 0
        self.assertEqual(self.dial.value_different(), 5)
        self.assertEqual(self.dial.last_value_call, 5)

    def test_time_valid_debounce_passed(self):
        self.mock_ticks_diff.return_value = 200 # Greater than typical debounce
        self.assertTrue(self.dial.time_valid(100, 0, 1, 1))
        self.assertEqual(self.dial.last_rotary_ms, self.mock_ticks_ms.return_value)

    def test_time_valid_debounce_not_passed(self):
        self.mock_ticks_diff.return_value = 50 # Less than typical debounce
        self.assertFalse(self.dial.time_valid(100, 0, 1, 1))
        self.assertEqual(self.dial.last_rotary_ms, 1000) # Should not update

    def test_time_valid_significant_turn(self):
        # difference > (direction * (1.3*min_turn))
        # 20 > (1 * (1.3 * 12)) => 20 > 15.6
        self.mock_ticks_diff.return_value = 50 # Debounce not passed
        self.assertTrue(self.dial.time_valid(100, 0, 20, 1))
        self.assertEqual(self.dial.last_rotary_ms, self.mock_ticks_ms.return_value)

    def test_event_check_no_difference(self):
        with patch.object(self.dial, 'value_different', return_value=False):
            self.assertIsNone(self.dial.event_check())

    def test_event_check_not_time_valid(self):
        with patch.object(self.dial, 'value_different', return_value=1):
            with patch.object(self.dial, 'time_valid', return_value=False):
                self.assertIsNone(self.dial.event_check())

    def test_event_check_valid(self):
        with patch.object(self.dial, 'value_different', return_value=1):
            with patch.object(self.dial, 'time_valid', return_value=True):
                self.assertTrue(self.dial.event_check())

class TestButton(unittest.TestCase):
    def setUp(self):
        # Patch ToggleInput's __init__ to avoid actual hardware initialization
        with patch('scripts.hardware_devices.input_device.ToggleInput.__init__', return_value=None):
            self.button = Button()
            self.button.rotary_encoder = MagicMock()
            self.button.button_pin = MagicMock()

        # Patch time functions
        self.patcher_ticks_ms = patch('scripts.hardware_devices.input_device.time.ticks_ms', return_value=1000)
        self.mock_ticks_ms = self.patcher_ticks_ms.start()
        self.addCleanup(self.patcher_ticks_ms.stop)

        self.patcher_ticks_diff = patch('scripts.hardware_devices.input_device.time.ticks_diff', return_value=0)
        self.mock_ticks_diff = self.patcher_ticks_diff.start()
        self.addCleanup(self.patcher_ticks_diff.stop)

        # Initialize Button specific attributes
        self.button.input_armed_button = True
        self.button.last_trigger_ms_button = 1000

    def test_init(self):
        self.assertTrue(self.button.input_armed_button)
        self.assertEqual(self.button.last_trigger_ms_button, 1000)

    def test_event_type_property(self):
        self.assertEqual(self.button.event_type, "button")

    @patch.object(Button, 'read_event_button', return_value=True)
    def test_event_property(self, mock_read_event_button):
        self.assertTrue(self.button.event)
        mock_read_event_button.assert_called_once()

    def test_read_event_button_not_pressed(self):
        self.button.button_pin.value.return_value = 1 # Not pressed
        self.button.input_armed_button = False # Was disarmed
        self.assertIsNone(self.button.read_event_button())
        self.assertTrue(self.button.input_armed_button) # Should re-arm

    def test_read_event_button_pressed_disarmed(self):
        self.button.button_pin.value.return_value = 0 # Pressed
        self.button.input_armed_button = False # Disarmed
        self.assertIsNone(self.button.read_event_button())
        self.assertFalse(self.button.input_armed_button) # Should remain disarmed

    def test_read_event_button_pressed_armed_not_time_valid(self):
        self.button.button_pin.value.return_value = 0 # Pressed
        self.button.input_armed_button = True # Armed
        with patch.object(self.button, 'check_time_valid', return_value=False):
            self.assertIsNone(self.button.read_event_button())
            self.assertTrue(self.button.input_armed_button) # Should remain armed

    def test_read_event_button_pressed_armed_time_valid(self):
        self.button.button_pin.value.return_value = 0 # Pressed
        self.button.input_armed_button = True # Armed
        self.mock_ticks_ms.return_value = 1500 # Simulate time passing
        with patch.object(self.button, 'check_time_valid', return_value=True):
            self.assertTrue(self.button.read_event_button())
            self.assertFalse(self.button.input_armed_button) # Should disarm
            self.assertEqual(self.button.last_trigger_ms_button, 1500) # Should update last trigger time

    def test_check_time_valid_true(self):
        self.mock_ticks_diff.return_value = INPUT_DEBOUNCE_MS + 10 # Time passed
        self.assertTrue(self.button.check_time_valid(0))

    def test_check_time_valid_false(self):
        self.mock_ticks_diff.return_value = INPUT_DEBOUNCE_MS - 10 # Not enough time passed
        self.assertFalse(self.button.check_time_valid(0))

    def test_check_time_valid_with_now_ms(self):
        self.mock_ticks_diff.return_value = INPUT_DEBOUNCE_MS + 10
        self.assertTrue(self.button.check_time_valid(0, now_ms=2000))
        self.mock_ticks_diff.assert_called_with(2000, 0) # Ensure now_ms is used

if __name__ == '__main__':
    unittest.main()
