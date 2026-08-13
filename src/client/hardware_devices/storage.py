import ujson

from config.config import DISPLAY_FILE, PRESET_FILE

class Storage:
    def __call__(self):
        display_file = None
        success_marker: bool = True
        file_error: None | Exception = None

        try:
            display_file = open(DISPLAY_FILE, "r")
            display_file.read()
        except Exception as err:
            success_marker = False
            file_error = err
        finally:
            if display_file is not None:
                display_file.close()

        return success_marker, file_error

    @staticmethod
    def ensure_dict(data, key=None):
        if data is None:
            return {"message": None}

        if type(data) == dict:
            return data

        if type(data) == bytes:
            data = data.decode("utf-8")

        if type(data) == list and key is not None:
            return {key: data}

        if type(data) == str:
            if data == "":
                return {"message": None}

            try:
                return ujson.loads(data)
            except Exception:
                return {"message": data}

        raise TypeError("Expected dict, str, bytes, or None")

    def read_display_data(self):
        display_file = None
        try:
            display_file = open(DISPLAY_FILE, "r")
            raw_data = display_file.read()
            return self.ensure_dict(raw_data)

        except Exception as error:
            print("Storage read error:", error)
            return {"message": None}

        finally:
            if display_file is not None:
                display_file.close()


    def read_preset_data(self):
        display_file = None
        try:
            display_file = open(PRESET_FILE, "r")
            raw_data = display_file.read()
            return self.ensure_dict(raw_data)
        except Exception as error:
            print("Storage write error:", error)
            return {"message": None}
        finally:
            if display_file is not None:
                display_file.close()


    def write_preset_data(self, preset_data):
        preset_file = None
        try:
            preset_data = self.ensure_dict(preset_data, key="presets")  # conv to dict
            preset_file = open(PRESET_FILE, "w")
            preset_file.write(ujson.dumps(preset_data))
            return preset_data
        except Exception as error:
            print("Storage write error:", error)
            return False
        finally:
            if preset_file is not None:
                preset_file.close()


    def write_display_data(self, display_data):
        display_file = None
        try:
            if type(display_data) != dict:
                display_data = {"message": display_data}
            display_data = self.ensure_dict(display_data, key="message")  # conv to dict
            display_file = open(DISPLAY_FILE, "w")
            display_file.write(ujson.dumps(display_data))
            return display_data
        except Exception as error:
            print("Storage read error:", error)
            return False
        finally:
            if display_file is not None:
                display_file.close()
