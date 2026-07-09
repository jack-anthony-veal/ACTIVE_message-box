import urequests as requests

from config import PRESET_PERSON, READ_PERSON


class MessageApiClient:
    def __init__(self, server_url: str, api_token: str):
        self.read_path: str = "/read/"
        self.send_path: str = "/send/"
        self.server_url: str = server_url
        self.api_token: str = api_token
        self.headers = {
            "content-type": "application/json",
            "box-token": self.api_token
        }

    def get_json(self, url): # returns a dict
        response = None
        try:
            response = requests.get(url, headers=self.headers)
            print(response.status_code)
            print(response.text)
            try:
                return response.json()
            except Exception as err:
                print("JSON parse error:", err)
                return None
        except Exception as err:
            print("HTTP error:", err)
            return None
        finally:
            if response is not None:
                response.close()

# ===================== ADD HANDLER FOR 202 ERROR
    def load_presets(self): # ALWAYS returns a list
        try:
            presets_url = self.server_url + "/presets/" + PRESET_PERSON
        except Exception as err:
            raise Exception(f'failed to lode presets {err}')

        response_data = self.get_json(presets_url)
        if response_data is not None:
            preset_list = response_data.get("presets")
            return True, list(preset_list)

        return False, ["No presets", "Upload on site"]



    def read_new_message(self): # Returns a dict
        read_url = self.server_url + self.read_path + READ_PERSON + "/"
        response_data = self.get_json(read_url)

        message_text = response_data.get("message") if response_data is not None else None

        if message_text is not None:
            print(response_data)
            return True, response_data

        return False, {"message": None}

    def send_preset(self, preset_index):
        ...