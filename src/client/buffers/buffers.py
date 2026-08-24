class Buffer:
    def __init__(self):
        self.message_buf: bytearray
        self.preset_buf: bytearray
        self.keyboard_buf: bytearray