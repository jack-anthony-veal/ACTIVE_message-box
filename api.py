import ujson
import urequests as requests
import gc

from config import PRESETS_JACK_URL, NO_PRESETS_RESP, READ_ELLA_URL, SEND_JACK_URL
from config.config import SERVER_URL, TOKEN

# TODO: add consts, update the server and allow for a better con management

class MessageApiClient:
    def __init__(self):
        self.api_token: str = TOKEN
        self.headers = {
            "content-type": "application/json",
            "box-token": TOKEN,
            "Connection": "close"
        }
        self.error_ms = 'api error'

    def get_json(self, url): # returns a dict
        session = None
        try:
            session = requests.get(url, headers=self.headers, timeout=5)
            if session.status_code < 200 or session.status_code >= 300:
                raise OSError("HTTP Error " + str(session.status_code))
            try:
                return session.json()
            except Exception:
                return session.text
        finally:
            if session is not None:
                try:
                    session.close()
                except Exception:
                    pass
            gc.collect() # free up ram used from tls


# ===================== ADD HANDLER FOR 202 ERROR
    def load_presets(self): # ALWAYS returns a list
        no_presets_resp = [NO_PRESETS_RESP]
        try:
            response_data = self.get_json(PRESETS_JACK_URL)
        except Exception:
            raise Exception(self.error_ms)

        if type(response_data) is not dict:
            return False, no_presets_resp

        preset_list = response_data.get("presets")
        if type(preset_list) not in (list, tuple):
            return False, no_presets_resp

        return True, preset_list


    def read_new_message(self): # Returns a dict
        url = READ_ELLA_URL

        try:
            response_data = self.get_json(url)
        except Exception:
            raise Exception(self.error_ms)

        if type(response_data) is dict and response_data.get("message") is not None:
            return True, response_data

        return False, {"message": None}

    def send_preset(self, preset_data):
        url = SEND_JACK_URL
        session = None
        try: # Implemented context manager to attempt to prevent timeouts
            body = {
                "text": preset_data
            }
            session = requests.post(url, headers=self.headers,data=ujson.dumps(body), timeout=30)
            code = session.status_code

            if code == 200:
                return True, None
            else:
                return False, "HTTP Error" + str(code)

        except Exception as error:
            return False, str(error)

        finally:
            if session is not None:
                try:
                    session.close()
                except Exception:
                    pass
            gc.collect()
