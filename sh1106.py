# MicroPython SH1106 OLED driver
import framebuf

class SH1106(framebuf.FrameBuffer):
    def __init__(self, width, height, i2c, addr=0x3C, rotate=0):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.inline_buffer = bytearray(2)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.inline_buffer[0] = 0x00
        self.inline_buffer[1] = cmd
        self.i2c.writeto(self.addr, self.inline_buffer)

    def init_display(self):
        for cmd in [
            0xAE, 0x02, 0x10, 0x40, 0x81, 0xCF, 0xA1, 0xC8,
            0xA6, 0xA8, 0x3F, 0xD3, 0x00, 0xD5, 0x80, 0xD9,
            0xF1, 0xDA, 0x12, 0xDB, 0x40, 0x8D, 0x14, 0xAF
        ]: self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x02) # SH1106 column offset fix
            self.write_cmd(0x10)
            # Write row block to I2C
            offset = page * self.width
            self.i2c.writeto_mem(self.addr, 0x40, self.buffer[offset:offset + self.width])

    def poweroff(self):
        self.write_cmd(0xAE) # Hardware command for Display OFF

    def poweron(self):
        self.write_cmd(0xAF)
