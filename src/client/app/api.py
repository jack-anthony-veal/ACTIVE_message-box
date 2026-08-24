import ujson
import urequests as requests
import gc

from config.config import (
    API_GET_TIMEOUT_S, API_POST_TIMEOUT_S, HTTP_SEND_SUCCESS_STATUS,
    HTTP_SUCCESS_MAX_EXCLUSIVE, HTTP_SUCCESS_MIN, NO_PRESETS_RESP,
    PRESETS_JACK_URL, READ_ELLA_URL, SEND_JACK_URL, TOKEN,
)


class MessageApiClient:
    def __init__(self):
        self.api_token: str = TOKEN
        self.headers = {
            "content-type": "application/json",
            "box-token": TOKEN,
            "Connection": "close"
        }
        self.error_ms = 'api error'

    def get_json(self, url):
        session = None
        try:
            session = requests.get(
                url, headers=self.headers, timeout=API_GET_TIMEOUT_S
            )
            if (
                session.status_code < HTTP_SUCCESS_MIN
                or session.status_code >= HTTP_SUCCESS_MAX_EXCLUSIVE
            ):
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
            gc.collect()

    def load_presets(self):
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
    def read_new_message(self):
        try:
            response_data = self.get_json(READ_ELLA_URL)
        except Exception:
            raise Exception(self.error_ms)

        if type(response_data) is dict and response_data.get("message") is not None:
            return True, response_data

        return False, {"message": None}

    def send_preset(self, preset_data):
        session = None
        try:
            body = {"text": preset_data}
            session = requests.post(
                SEND_JACK_URL,
                headers=self.headers,
                data=ujson.dumps(body),
                timeout=API_POST_TIMEOUT_S,
            )
            code = session.status_code

            if code == HTTP_SEND_SUCCESS_STATUS:
                return True, None
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
