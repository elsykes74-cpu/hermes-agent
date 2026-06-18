import io
import os
import json
import random
import requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
QUICKKICK_API_URL = os.environ["QUICKKICK_API_URL"].rstrip("/")
QUICKKICK_API_KEY = os.environ["QUICKKICK_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]

with open("topics/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

today = datetime.now()
random.seed(today.strftime("%Y-%m-%d"))
topic = random.choice(topics)

print(f"Today's topic: {topic}")

openrouter_headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/elsykes74-cpu/elvis-daily-script",
    "X-Title": "The King Lives - Elvis Daily Script",
}

# ── 1. Script ─────────────────────────────────────────────────────────────────

script_response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=openrouter_headers,
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the head writer for The King Lives — a faceless Elvis Presley "
                    "documentary YouTube channel. Write a single 60-second narration script "
                    "about the assigned topic.\n\n"
                    "STRICT RULES:\n"
                    "- 130 to 150 words exactly\n"
                    "- No blank lines between sentences — one continuous flowing block of text\n"
                    "- No stage directions, scene notes, labels, or headers\n"
                    "- No markdown formatting of any kind\n"
                    "- Historically accurate — do not invent facts\n"
                    "- Open with a date, place, or shocking statement — never Elvis's name first\n"
                    "- Cinematic documentary tone — David Attenborough meets true crime\n"
                    "- End on an emotional gut-punch closing line\n"
                    "- Output the raw script text and absolutely nothing else"
                ),
            },
            {"role": "user", "content": f"Today's topic: {topic}"},
        ],
    },
    timeout=60,
)
script_response.raise_for_status()
script = script_response.json()["choices"][0]["message"]["content"].strip()

word_count = len(script.split())
print(f"Script generated ({word_count} words)")
print(f"\n--- SCRIPT PREVIEW ---\n{script[:150]}...\n")

# ── 2. Scene breakdown ────────────────────────────────────────────────────────

scene_response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=openrouter_headers,
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a documentary video editor. You receive a 60-second narration "
                    "script and break it into exactly 7 scenes with timestamps and visual "
                    "directions.\n\n"
                    "STRICT RULES:\n"
                    "- Exactly 7 scenes\n"
                    "- Timestamps start at 00:00 and end at 01:00 exactly\n"
                    "- Visual direction is one concrete sentence describing the image or footage\n"
                    "- Visual directions must be specific enough to use as image search queries "
                    "or Higgsfield AI video generation prompts\n"
                    "- Do not invent content — only use words from the script\n"
                    "- Output only the scene breakdown in this exact format, nothing else:\n\n"
                    "Scene 1 | 00:00 - 00:05\n"
                    "[script excerpt]\n"
                    "Visual direction: [one sentence]\n\n"
                    "Scene 2 | 00:05 - 00:12\n"
                    "[script excerpt]\n"
                    "Visual direction: [one sentence]\n\n"
                    "Continue through Scene 7 ending exactly at 01:00"
                ),
            },
            {"role": "user", "content": f"Break this script into scenes:\n\n{script}"},
        ],
    },
    timeout=60,
)
scene_response.raise_for_status()
scene_breakdown = scene_response.json()["choices"][0]["message"]["content"].strip()

print("Scene breakdown generated")

# ── 3. Production document ────────────────────────────────────────────────────

date_str = today.strftime(f"%B {today.day}, %Y")
divider = "=" * 48

production_doc = "\n".join([
    divider,
    "THE KING LIVES — DAILY PRODUCTION DOCUMENT",
    f"Date: {date_str}",
    f"Topic: {topic}",
    divider,
    "",
    "FULL SCRIPT:",
    script,
    "",
    divider,
    "",
    "SCENE BREAKDOWN:",
    scene_breakdown,
    "",
    divider,
    "PRODUCTION NOTES:",
    "ElevenLabs: speed 0.88 | stability 70% | similarity 65% |",
    "style exaggeration off | speaker boost on",
    "Channel: The King Lives",
    "Format: Faceless documentary | 9:16 vertical",
    divider,
    "",
])

# ── 4. Google Drive upload ────────────────────────────────────────────────────

creds = service_account.Credentials.from_service_account_info(
    json.loads(GOOGLE_CREDENTIALS_JSON),
    scopes=["https://www.googleapis.com/auth/drive"],
)
drive = build("drive", "v3", credentials=creds)

results = drive.drives().list(
    q="name='Elvis Scripts'",
    fields="drives(id, name)",
    pageSize=10,
).execute()
shared_drives = results.get("drives", [])
if not shared_drives:
    raise RuntimeError(
        "'Elvis Scripts' shared drive not found. Create a Shared Drive with that name, "
        "add the service account as Content Manager, then retry."
    )
folder_id = shared_drives[0]["id"]

file_name = today.strftime("%Y-%m-%d") + "_Elvis_Production.txt"
drive_file = drive.files().create(
    body={"name": file_name, "parents": [folder_id], "mimeType": "text/plain"},
    media_body=MediaIoBaseUpload(
        io.BytesIO(production_doc.encode("utf-8")),
        mimetype="text/plain",
    ),
    fields="id, name",
    supportsAllDrives=True,
).execute()

print(f"Uploaded to Drive: {drive_file['name']} (ID: {drive_file['id']})")

# ── 5. QuickKick delivery ─────────────────────────────────────────────────────

message = f"We are going to do an Elvis Presley video.\n\nSCRIPT:\n\n{script}"

quickkick_response = requests.post(
    f"{QUICKKICK_API_URL}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {QUICKKICK_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "hermes-agent",
        "messages": [{"role": "user", "content": message}],
    },
    timeout=120,
)

print(f"QuickKick status: {quickkick_response.status_code}")
if not quickkick_response.ok:
    print(f"QuickKick error body: {quickkick_response.text}")
quickkick_response.raise_for_status()
print("Script delivered to QuickKick successfully")

print("\n--- SUMMARY ---")
print(f"Topic     : {topic}")
print(f"Word count: {word_count}")
print(f"Drive file: {file_name}")
print(f"QuickKick : delivered")
