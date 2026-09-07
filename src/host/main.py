import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI(title="Message Box")

SECRET = os.environ.get("MESSAGE_BOX_TOKEN")
HOST_ROOT = Path(__file__).resolve().parent
DATA = HOST_ROOT / "data"
DATA.mkdir(exist_ok=True)

PRESETS_FILE = DATA / "presets.json"
UPDATE_RESULTS_FILE = DATA / "update-results.json"
UPDATE_ROOT = HOST_ROOT / "updates" / "current"
UPDATE_MANIFEST_FILE = UPDATE_ROOT / "manifest.json"
INDEX_FILE = HOST_ROOT / "static" / "index.html"
PEOPLE = {"jack", "ella"}
MAX_PRESETS = 5
MAX_TEXT_LENGTH = 4096
UPDATE_RESULTS_LIMIT = 100
_DATA_LOCK = threading.Lock()


class Message(BaseModel):
    text: str


class Preset(BaseModel):
    text: str


class UpdateResult(BaseModel):
    device: str
    version: str
    success: bool
    detail: str = ""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def check_token(box_token: str | None):
    if SECRET is None or box_token != SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad token",
        )


def check_person(person: str):
    person = person.lower()
    if person not in PEOPLE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown person",
        )
    return person


def atomic_json_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with open(temporary, "w", encoding="utf-8") as destination:
        json.dump(data, destination, indent=2)
        destination.flush()
        os.fsync(destination.fileno())
    os.replace(temporary, path)


def slot_file(sender):
    return DATA / (sender + ".slot.json")


def load_slot(sender):
    path = slot_file(sender)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as source:
            slot = json.load(source)
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(slot, dict):
        return None
    required = ("id", "sender", "text", "utc")
    if any(not isinstance(slot.get(key), str) for key in required):
        return None
    return slot


def load_presets():
    if not PRESETS_FILE.exists():
        return {"jack": [], "ella": []}
    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as source:
            data = json.load(source)
    except (OSError, ValueError, TypeError):
        data = {}
    return {
        person: list(data.get(person, []))[:MAX_PRESETS]
        if isinstance(data.get(person, []), list)
        else []
        for person in PEOPLE
    }


def save_presets(data):
    clean = {}
    for person in PEOPLE:
        values = data.get(person, [])
        if not isinstance(values, list) or len(values) > MAX_PRESETS:
            raise ValueError("presets must contain zero to five entries")
        clean[person] = values
    atomic_json_write(PRESETS_FILE, clean)


def clean_text(text, label):
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=label + " cannot be empty",
        )
    if len(text.encode("utf-8")) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=label + " is too large",
        )
    return text


def clean_preset(text: str):
    return clean_text(text, "Preset")


def safe_update_file(relative_path):
    normalised = PurePosixPath(str(relative_path).replace("\\", "/"))
    if normalised.is_absolute() or ".." in normalised.parts or not normalised.parts:
        raise HTTPException(status_code=404, detail="Update file not found")
    root = (UPDATE_ROOT / "files").resolve()
    path = root.joinpath(*normalised.parts).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Update file not found")
    return path


@app.get("/")
def home():
    return FileResponse(INDEX_FILE)


@app.post("/send/{person}")
def send(person: str, msg: Message, box_token: str | None = Header(default=None)):
    check_token(box_token)
    sender = check_person(person)
    slot = {
        "id": uuid.uuid4().hex,
        "sender": sender,
        "text": clean_text(msg.text, "Message"),
        "utc": utc_now(),
    }
    with _DATA_LOCK:
        atomic_json_write(slot_file(sender), slot)
    return {"saved": True, "message": slot}


@app.get("/read/{person}")
def read(person: str, box_token: str | None = Header(default=None)):
    check_token(box_token)
    sender = check_person(person)
    with _DATA_LOCK:
        slot = load_slot(sender)
    return {"message": slot}


@app.post("/ack/{person}/{message_id}")
def acknowledge(
    person: str,
    message_id: str,
    box_token: str | None = Header(default=None),
):
    check_token(box_token)
    sender = check_person(person)
    with _DATA_LOCK:
        current = load_slot(sender)
        if current is None or current["id"] != message_id:
            return {"acknowledged": False, "current_id": current and current["id"]}
        try:
            slot_file(sender).unlink()
        except FileNotFoundError:
            return {"acknowledged": False, "current_id": None}
    return {"acknowledged": True, "id": message_id}


@app.get("/presets/{person}")
def get_presets(person: str, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    with _DATA_LOCK:
        data = load_presets()
    return {"person": person, "presets": data[person]}


@app.post("/presets/{person}")
def add_preset(person: str, preset: Preset, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    text = clean_preset(preset.text)
    with _DATA_LOCK:
        data = load_presets()
        if len(data[person]) >= MAX_PRESETS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum {} presets".format(MAX_PRESETS),
            )
        if text in data[person]:
            raise HTTPException(status_code=400, detail="Preset already exists")
        data[person].append(text)
        save_presets(data)
    return {"saved": True, "person": person, "presets": data[person]}


@app.put("/presets/{person}/{index}")
def edit_preset(
    person: str,
    index: int,
    preset: Preset,
    box_token: str | None = Header(default=None),
):
    check_token(box_token)
    person = check_person(person)
    text = clean_preset(preset.text)
    with _DATA_LOCK:
        data = load_presets()
        if index < 0 or index >= len(data[person]):
            raise HTTPException(status_code=404, detail="Preset not found")
        if text in data[person] and data[person][index] != text:
            raise HTTPException(status_code=400, detail="Preset already exists")
        data[person][index] = text
        save_presets(data)
    return {"saved": True, "person": person, "presets": data[person]}


@app.delete("/presets/{person}/{index}")
def delete_preset(person: str, index: int, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    with _DATA_LOCK:
        data = load_presets()
        if index < 0 or index >= len(data[person]):
            raise HTTPException(status_code=404, detail="Preset not found")
        removed = data[person].pop(index)
        save_presets(data)
    return {"deleted": removed, "person": person, "presets": data[person]}


@app.get("/update/manifest")
def update_manifest(box_token: str | None = Header(default=None)):
    check_token(box_token)
    if not UPDATE_MANIFEST_FILE.is_file():
        raise HTTPException(status_code=404, detail="No update is published")
    try:
        with open(UPDATE_MANIFEST_FILE, "r", encoding="utf-8") as source:
            manifest = json.load(source)
    except (OSError, ValueError, TypeError):
        raise HTTPException(status_code=500, detail="Invalid update manifest")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise HTTPException(status_code=500, detail="Invalid update manifest")
    return manifest


@app.get("/update/file/{relative_path:path}")
def update_file(relative_path: str, box_token: str | None = Header(default=None)):
    check_token(box_token)
    return FileResponse(safe_update_file(relative_path))


@app.post("/update/results")
def add_update_result(
    result: UpdateResult,
    box_token: str | None = Header(default=None),
):
    check_token(box_token)
    entry = result.model_dump()
    entry["utc"] = utc_now()
    with _DATA_LOCK:
        try:
            with open(UPDATE_RESULTS_FILE, "r", encoding="utf-8") as source:
                results = json.load(source)
        except (OSError, ValueError, TypeError):
            results = []
        if not isinstance(results, list):
            results = []
        results.append(entry)
        results = results[-UPDATE_RESULTS_LIMIT:]
        atomic_json_write(UPDATE_RESULTS_FILE, results)
    return {"saved": True, "count": len(results)}


@app.get("/update/results")
def get_update_results(box_token: str | None = Header(default=None)):
    check_token(box_token)
    try:
        with open(UPDATE_RESULTS_FILE, "r", encoding="utf-8") as source:
            results = json.load(source)
    except (OSError, ValueError, TypeError):
        results = []
    return {"results": results[-UPDATE_RESULTS_LIMIT:]}
