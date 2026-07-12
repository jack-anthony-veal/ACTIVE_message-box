import ujson
import urequests as requests
import gc
from config.config import SERVER_URL, TOKEN

# TODO: add consts, update the server and allow for a better con management


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
        # Implemented context manager to attempt to prevent timeouts
        session = requests.get(url, headers=self.headers, timeout=5)
        print(session.status_code)
        print(session.text)
        try:
            data = session.json()

        except Exception as err:
            print("JSON parse error:", err)
            data=session.text

        try:
            session.close()
        except Exception as err:
            print("socket couldnt close")

        gc.collect() # free up ram used from tls
        return data


# ===================== ADD HANDLER FOR 202 ERROR
    def load_presets(self): # ALWAYS returns a list
        response_code = None
        presets_url = self.server_url + "/presets/jack/"
        try:
            response_data = self.get_json(presets_url)

        except Exception as err:
            raise Exception(err)

        if type(response_data) is not dict:
            try:
                return False, list(str(response_data))
            except:
                return False, 'Error opening api data'


        if response_data is not None and type(response_data) is dict:
            try:
                preset_list = response_data.get("presets")

            except Exception as err:
                raise Exception(err)


            return True, list(preset_list)

        else:
            return False, ["No presets", "Upload on site"]



    def read_new_message(self): # Returns a dict
        read_url = self.server_url + '/read/ella'
        try:
            response_data = self.get_json(read_url)
        except Exception as err:
            raise Exception(err)

        message_text = response_data.get("message") if response_data is not None else None

        if message_text is not None:
            print(response_data)
            return True, response_data

        return False, {"message": None}

    def send_preset(self, preset_data):
        session=None
        url = SERVER_URL + '/send/ella'
        try: # Implemented context manager to attempt to prevent timeouts
            body = {
                "text": preset_data
            }
            session = requests.post(url, headers=self.headers,data=ujson.dumps(body), timeout=30)
            print(session.status_code)

            if session.status_code == 200:
                session.close()
                return True, None

            else:
                return False, "HTTP Error" + str(session.status_code)

        except Exception as err:
            print(str(err))
            return False, "Data rejected"

        finally:
            if session is not None: session.close()

