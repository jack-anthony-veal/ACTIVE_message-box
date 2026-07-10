import urequests as requests

from config.config import PRESET_PERSON, READ_PERSON, SERVER_URL, TOKEN


class MessageApiClient:
    def __init__(self):
        self.read_path: str = "/read/"
        self.send_path: str = "/send/"
        self.server_url: str = SERVER_URL
        self.api_token: str = TOKEN
        self.headers = {
            "content-type": "application/json",
            "box-token": TOKEN,
            "Connection": "close"
        }

    def get_json(self, url): # returns a dict
        data = None
        session = None
        try: # Implemented context manager to attempt to prevent timeouts
            session = requests.get(url, headers=self.headers, timeout=5)
            print(session.status_code)
            print(session.text)
            try:
                data = session.json()

            except Exception as err:
                print("JSON parse error:", err)
                data=session.text
                session.close()

        except Exception as err:
            print("HTTP error:", err)
            gc.collect()
            return

        finally:
            if data is not None:
                session.close()

        gc.collect() # free up ram used from tls
        return data


# ===================== ADD HANDLER FOR 202 ERROR
    def load_presets(self): # ALWAYS returns a list
        try:
            presets_url = self.server_url + "/presets/" + PRESET_PERSON
        except Exception as err:
            raise Exception(f'failed to lode presets {err}')

        presets_url = self.server_url + "/presets/jack/"
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
