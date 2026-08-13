import ujson


# TODO : Remove half of this shit or make it proper idk wtf it does

def menu_str_payload(payload):
    updated_str = ''
    for x in str(payload).split("\n"):
        updated_str += x
    wrapped_lines = wrap_text(updated_str)
    return wrapped_lines

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


def wrap_text(text: str, width=16, max_lines=None):
    text = str(text)
    wrapped_lines = []

    for raw_line in text.split("\n"):
        if raw_line == "":
            wrapped_lines.append("")
        else:
            for start in range(0, len(raw_line), width):
                wrapped_lines.append(raw_line[start:start + width])
                if max_lines is not None and len(wrapped_lines) >= max_lines:
                    return wrapped_lines

        if max_lines is not None and len(wrapped_lines) >= max_lines:
            return wrapped_lines

    return wrapped_lines
