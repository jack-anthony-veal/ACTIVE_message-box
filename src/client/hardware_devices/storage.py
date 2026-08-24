import ujson

from config.config import (
    DISPLAY_FILE, MESSAGE_STORAGE_KEY, PRESET_FILE, PRESETS_STORAGE_KEY,
)


class Storage:
    def __call__(self):
        try:
            with open(DISPLAY_FILE, "r") as display_file:
                display_file.read()
            return True, None
        except Exception as error:
            return False, error

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
            with open(path, "w") as destination:
                destination.write(ujson.dumps(data))
            return data
        except Exception as error:
            print("Storage write error:", error)
            return False

    def read_display_data(self):
        return self._read(DISPLAY_FILE, {MESSAGE_STORAGE_KEY: None})

    def read_preset_data(self):
        return self._read(PRESET_FILE, {PRESETS_STORAGE_KEY: []})

    def write_preset_data(self, preset_data):
        return self._write(PRESET_FILE, preset_data, PRESETS_STORAGE_KEY)

    def write_display_data(self, display_data):
        return self._write(DISPLAY_FILE, display_data, MESSAGE_STORAGE_KEY)
