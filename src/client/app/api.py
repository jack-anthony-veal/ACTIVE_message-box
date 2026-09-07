import gc
import ujson
import urequests as requests

try:
    from config.config import (
        ACK_MESSAGE_URL, API_GET_TIMEOUT_S, API_POST_TIMEOUT_S,
        HTTP_SUCCESS_MAX_EXCLUSIVE, HTTP_SUCCESS_MIN, MAX_PRESETS,
        NO_PRESETS_RESP, PRESETS_URL, READ_MESSAGE_URL, SEND_MESSAGE_URL,
        TOKEN, UPDATE_FILE_URL, UPDATE_MANIFEST_URL, UPDATE_RESULT_URL,
    )
except ImportError:
    from config.config import (
        API_GET_TIMEOUT_S, API_POST_TIMEOUT_S, HTTP_SUCCESS_MAX_EXCLUSIVE,
        HTTP_SUCCESS_MIN, NO_PRESETS_RESP, PRESETS_JACK_URL,
        READ_ELLA_URL, SEND_JACK_URL, TOKEN,
    )

    PRESETS_URL = PRESETS_JACK_URL
    READ_MESSAGE_URL = READ_ELLA_URL
    SEND_MESSAGE_URL = SEND_JACK_URL
    ACK_MESSAGE_URL = READ_MESSAGE_URL.replace("/read/", "/ack/")
    base_url = READ_MESSAGE_URL.split("/read/", 1)[0]
    UPDATE_MANIFEST_URL = base_url + "/update/manifest"
    UPDATE_FILE_URL = base_url + "/update/file"
    UPDATE_RESULT_URL = base_url + "/update/results"
    MAX_PRESETS = 5


class MessageApiClient:
    def __init__(self):
        self.api_token = TOKEN
        self.headers = {
            "content-type": "application/json",
            "box-token": TOKEN,
            "Connection": "close",
        }
        self.error_ms = "api error"

    @staticmethod
    def _close(session):
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
        gc.collect()

    @staticmethod
    def _check_status(session):
        if (
            session.status_code < HTTP_SUCCESS_MIN
            or session.status_code >= HTTP_SUCCESS_MAX_EXCLUSIVE
        ):
            raise OSError("HTTP Error " + str(session.status_code))

    def get_json(self, url):
        session = None
        try:
            session = requests.get(
                url, headers=self.headers, timeout=API_GET_TIMEOUT_S
            )
            self._check_status(session)
            try:
                return session.json()
            except Exception:
                return session.text
        finally:
            self._close(session)

    def post_json(self, url, body):
        session = None
        try:
            session = requests.post(
                url,
                headers=self.headers,
                data=ujson.dumps(body),
                timeout=API_POST_TIMEOUT_S,
            )
            self._check_status(session)
            try:
                return session.json()
            except Exception:
                return session.text
        finally:
            self._close(session)

    def get_bytes(self, url):
        session = None
        try:
            session = requests.get(
                url, headers=self.headers, timeout=API_POST_TIMEOUT_S
            )
            self._check_status(session)
            return bytes(session.content)
        finally:
            self._close(session)

    def load_presets(self):
        no_presets = [NO_PRESETS_RESP]
        try:
            response_data = self.get_json(PRESETS_URL)
        except Exception:
            raise Exception(self.error_ms)
        if type(response_data) is not dict:
            return False, no_presets
        presets = response_data.get("presets")
        if type(presets) not in (list, tuple) or len(presets) > MAX_PRESETS:
            return False, no_presets
        return True, list(presets)

    def read_new_message(self):
        try:
            response_data = self.get_json(READ_MESSAGE_URL)
        except Exception:
            raise Exception(self.error_ms)
        if type(response_data) is not dict:
            return False, {"message": None}
        message = response_data.get("message")
        if type(message) is not dict:
            return False, {"message": None}
        required = ("id", "sender", "text", "utc")
        if any(type(message.get(key)) is not str for key in required):
            return False, {"message": None}
        return True, response_data

    def acknowledge_message(self, message_id):
        try:
            response = self.post_json(
                ACK_MESSAGE_URL + "/" + str(message_id), {}
            )
        except Exception:
            return False
        return type(response) is dict and response.get("acknowledged") is True

    def send_message(self, text):
        try:
            response = self.post_json(SEND_MESSAGE_URL, {"text": text})
            if type(response) is dict and response.get("saved") is True:
                return True, response.get("message")
            if response is None or response == "":
                return True, None
            return False, "Invalid response"
        except Exception as error:
            return False, str(error)

    def send_preset(self, preset_data):
        return self.send_message(preset_data)

    def get_update_manifest(self):
        return self.get_json(UPDATE_MANIFEST_URL)

    def download_update_file(self, relative_path):
        return self.get_bytes(UPDATE_FILE_URL + "/" + relative_path)

    def report_update_result(self, version, success, detail, device):
        return self.post_json(
            UPDATE_RESULT_URL,
            {
                "device": device,
                "version": version,
                "success": bool(success),
                "detail": str(detail),
            },
        )
