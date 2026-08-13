
"""
ACCESS
- POST
https://url/send/person
- GET
https://url/read/person
https://url/presets/person
GET / POST /
https://url/presets/person/index
PUT / DELETE


"""

import json
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

SECRET = "password"
DATA = Path("data")
DATA.mkdir(exist_ok=True)

PRESETS_FILE = DATA / "presets.json"
PEOPLE = {"jack", "ella"}
MAX_PRESETS = 5
OLED_COLS = 16
OLED_ROWS = 6


class Message(BaseModel):
    text: str


class Preset(BaseModel):
    text: str


def check_token(box_token: str | None):
    if box_token != SECRET:
        raise HTTPException(status_code=401, detail="Bad token")


def check_person(person: str):
    person = person.lower()
    if person not in PEOPLE:
        raise HTTPException(status_code=404, detail="Unknown person")
    return person


def load_presets():
    if not PRESETS_FILE.exists():
        return {"jack": [], "ella": []}

    with open(PRESETS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "jack": data.get("jack", []),
        "ella": data.get("ella", []),
    }


def save_presets(data):
    with open(PRESETS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def clean_preset(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if text == "":
        raise HTTPException(status_code=400, detail="Preset cannot be empty")

    rows_used = 0
    for line in text.split("\n"):
        rows_used += max(1, (len(line) + OLED_COLS - 1) // OLED_COLS)

    if rows_used > OLED_ROWS:
        raise HTTPException(
            status_code=400,
            detail="Preset must fit 128x64 display: max 16 chars x 6 lines",
        )

    return text


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/send/{person}")
def send(person: str, msg: Message, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    file = DATA / f"{person}.txt"
    file.write_text(msg.text, encoding="utf-8")
    return {"saved": True, "person": person}


@app.get("/read/{person}")
def read(person: str, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    file = DATA / f"{person}.txt"

    if not file.exists():
        return {"message": None}

    text = file.read_text(encoding="utf-8")
    if text == "":
        return {"message": None}

    file.write_text("", encoding="utf-8")
    return {"message": text}


@app.get("/presets/{person}")
def get_presets(person: str, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    data = load_presets()
    return {"person": person, "presets": data[person]}


@app.post("/presets/{person}")
def add_preset(person: str, preset: Preset, box_token: str | None = Header(default=None)):
    check_token(box_token)
    person = check_person(person)
    text = clean_preset(preset.text)
    data = load_presets()

    if len(data[person]) >= MAX_PRESETS:
        raise HTTPException(status_code=400, detail="Maximum 5 presets")

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
    data = load_presets()

    if index < 0 or index >= len(data[person]):
        raise HTTPException(status_code=404, detail="Preset not found")

    removed = data[person].pop(index)
    save_presets(data)
    return {"deleted": removed, "person": person, "presets": data[person]}
