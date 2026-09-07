import importlib.util
import os
import unittest

from fastapi import HTTPException, status


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST_MAIN = os.path.join(ROOT, "host", "main.py")
TEST_TOKEN = "local-test-token"

os.environ["MESSAGE_BOX_TOKEN"] = TEST_TOKEN
spec = importlib.util.spec_from_file_location("message_box_host", HOST_MAIN)
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)


class TestHostConfiguration(unittest.TestCase):
    def test_token_comes_from_environment(self):
        self.assertEqual(host.SECRET, TEST_TOKEN)
        host.check_token(TEST_TOKEN)
        with self.assertRaises(HTTPException) as raised:
            host.check_token("incorrect")
        self.assertEqual(
            raised.exception.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_static_index_path_is_module_relative(self):
        self.assertTrue(host.INDEX_FILE.is_file())
        self.assertEqual(host.INDEX_FILE.parent.name, "static")

    def test_preset_text_is_scrollable_but_bounded(self):
        long_preset = "x" * host.MAX_TEXT_LENGTH
        self.assertEqual(host.clean_preset(long_preset), long_preset)
        with self.assertRaises(HTTPException):
            host.clean_preset(long_preset + "x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
