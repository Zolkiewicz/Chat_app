import json

ENCODING = 'utf-8'
DELIMITER = '\n'

def encode_message(msg_type: str, payload: dict = None) -> bytes:
    data = {
        "type": msg_type,
        "payload": payload or {}
    }
    raw_json = json.dumps(data) + DELIMITER
    return raw_json.encode(ENCODING)

def decode_messages(buffer: str) -> tuple[list[dict], str]:
    messages = []
    while DELIMITER in buffer:
        line, buffer = buffer.split(DELIMITER, 1)
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"[PARSER ERROR] Invalid JSON: {line}")
    return messages, buffer