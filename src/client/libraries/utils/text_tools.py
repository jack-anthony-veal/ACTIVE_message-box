import ujson

def message_from_payload(payload): # Converts all payloads to str
    if payload is None:
        return "No new messages!"

    if type(payload) == list:
        payload = "".join(str(i) for i in payload)

    if type(payload) in (int, bool, float):
        message = str(payload)
        return message

    if type(payload) == dict:
        message = payload.get("message")

        if message is None:
            return "No new messages!"

        return str(message)

    if type(payload) == bytes:
        payload = payload.decode("utf-8")

    if type(payload) == str:
        try:
            stripped_payload = payload.strip()
            if not stripped_payload.startswith("{"):
                return payload

            parsed_payload = ujson.loads(stripped_payload)
            message = parsed_payload.get("message")

            if message is None:
                return "No new messages!"

            return str(message)
        except Exception as err:
            print(str(err))
            return payload

    return str(payload)
