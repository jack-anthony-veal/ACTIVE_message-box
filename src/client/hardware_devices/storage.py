import ujson

try:
    from config.config import (
        DISPLAY_FILE, MESSAGES_FILE, MESSAGE_STORAGE_KEY, PRESET_FILE,
        PRESETS_STORAGE_KEY,
    )
except ImportError:
    from config.config import (
        DISPLAY_FILE, MESSAGE_STORAGE_KEY, PRESET_FILE, PRESETS_STORAGE_KEY,
    )

    MESSAGES_FILE = DISPLAY_FILE + ".jsonl"


class Storage:
    def __call__(self):
        try:
            self._recover_messages_file()
            self._ensure_parent(MESSAGES_FILE)
            with open(MESSAGES_FILE, "a") as messages_file:
                messages_file.write("")
            return True, None
        except Exception as error:
            return False, error

    @staticmethod
    def _ensure_parent(path):
        import os

        parts = str(path).replace("\\", "/").split("/")[:-1]
        current = ""
        for part in parts:
            if not part or part == ".":
                continue
            current = current + "/" + part if current else part
            try:
                os.mkdir(current)
            except OSError:
                pass

    @staticmethod
    def ensure_dict(data, key=None):
        if data is None:
            return {MESSAGE_STORAGE_KEY: None}
        if type(data) == dict:
            return data
        if type(data) == bytes:
            data = data.decode("utf-8")
        if type(data) == list and key is not None:
            return {key: data}
        if type(data) == str:
            if data == "":
                return {MESSAGE_STORAGE_KEY: None}
            try:
                return ujson.loads(data)
            except Exception:
                return {MESSAGE_STORAGE_KEY: data}
        raise TypeError("Expected dict, str, bytes, list with key, or None")

    @staticmethod
    def valid_message(message):
        if type(message) is not dict:
            return False
        for key in ("id", "sender", "text", "utc"):
            if type(message.get(key)) is not str:
                return False
        return bool(message["id"])

    def _read(self, path, fallback):
        try:
            with open(path, "r") as source:
                return self.ensure_dict(source.read())
        except Exception as error:
            print("Storage read error:", error)
            return fallback

    def _write(self, path, data, key):
        try:
            data = self.ensure_dict(data, key=key)
            self._ensure_parent(path)
            with open(path, "w") as destination:
                destination.write(ujson.dumps(data))
            return data
        except Exception as error:
            print("Storage write error:", error)
            return False

    @staticmethod
    def _decode_message(line):
        try:
            value = ujson.loads(line.decode("utf-8"))
        except Exception:
            return None
        return value if Storage.valid_message(value) else None

    @staticmethod
    def _recover_messages_file():
        import os

        temporary = MESSAGES_FILE + ".repair"
        try:
            os.stat(temporary)
        except OSError:
            return
        try:
            os.stat(MESSAGES_FILE)
        except OSError:
            os.rename(temporary, MESSAGES_FILE)
            return
        try:
            os.remove(temporary)
        except OSError:
            pass

    def _message_records(self):
        self._recover_messages_file()
        try:
            with open(MESSAGES_FILE, "rb") as source:
                for line in source:
                    value = self._decode_message(line)
                    if value is not None:
                        yield value
        except OSError:
            return

    def read_messages(self):
        return list(self._message_records())

    def newest_message(self):
        newest = None
        for message in self._message_records():
            newest = message
        return newest

    def has_message(self, message_id):
        for message in self._message_records():
            if message["id"] == message_id:
                return True
        return False

    def _discard_partial_tail(self):
        import os

        self._recover_messages_file()
        try:
            with open(MESSAGES_FILE, "rb") as source:
                source.seek(0, 2)
                end = source.tell()
                if end == 0:
                    return
                source.seek(end - 1)
                if source.read(1) == b"\n":
                    return
                line_start = end - 1
                while line_start > 0:
                    source.seek(line_start - 1)
                    if source.read(1) == b"\n":
                        break
                    line_start -= 1
                source.seek(line_start)
                tail = source.read(end - line_start)
        except OSError:
            return

        if len(tail) <= 8192 and self._decode_message(tail) is not None:
            with open(MESSAGES_FILE, "ab") as destination:
                destination.write(b"\n")
            return

        temporary = MESSAGES_FILE + ".repair"
        with open(MESSAGES_FILE, "rb") as source:
            with open(temporary, "wb") as destination:
                remaining = line_start
                while remaining:
                    block = source.read(min(1024, remaining))
                    if not block:
                        break
                    destination.write(block)
                    remaining -= len(block)
        try:
            os.remove(MESSAGES_FILE)
        except OSError:
            pass
        os.rename(temporary, MESSAGES_FILE)

    def append_message(self, message):
        if not self.valid_message(message):
            raise ValueError("invalid message record")
        if self.has_message(message["id"]):
            return True
        self._ensure_parent(MESSAGES_FILE)
        self._discard_partial_tail()
        encoded = (ujson.dumps(message) + "\n").encode("utf-8")
        with open(MESSAGES_FILE, "ab") as destination:
            destination.write(encoded)
        if not self.has_message(message["id"]):
            raise OSError("message append validation failed")
        return True

    def read_display_data(self):
        newest = self.newest_message()
        if newest is not None:
            return {MESSAGE_STORAGE_KEY: newest["text"], "record": newest}
        return self._read(DISPLAY_FILE, {MESSAGE_STORAGE_KEY: None})

    def read_preset_data(self):
        return self._read(PRESET_FILE, {PRESETS_STORAGE_KEY: []})

    def write_preset_data(self, preset_data):
        return self._write(PRESET_FILE, preset_data, PRESETS_STORAGE_KEY)

    def write_display_data(self, display_data):
        if type(display_data) is dict:
            message = display_data.get("message", display_data)
            if self.valid_message(message):
                return self.append_message(message)
        return self._write(DISPLAY_FILE, display_data, MESSAGE_STORAGE_KEY)
