import os
import json
import random
import requests
from datetime import datetime

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
LADYJAYE_BOT_TOKEN = os.environ["LADYJAYE_BOT_TOKEN"]
QUICKKICK_CHAT_ID = os.environ["QUICKKICK_CHAT_ID"].strip()

with open("topics/topics.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

random.seed(datetime.now().strftime("%Y-%m-%d"))
topic = random.choice(topics)

print(f"Today's topic: {topic}")

system_prompt = """You are the head writer for The King Lives — a faceless Elvis Presley documentary YouTube channel. Write a single 60-second narration script about the assigned topic.

STRICT RULES:
- 130 to 150 words exactly
- No blank lines between sentences — one continuous flowing block of text
- No stage directions, scene notes, labels, or headers
- No markdown formatting of any kind
- Historically accurate — do not invent facts
- Open with a date, place, or shocking statement — never Elvis's name first
- Cinematic documentary tone — David Attenborough meets true crime
- End on an emotional gut-punch closing line
- Output the raw script text and absolutely nothing else"""

user_prompt = f"Today's topic: {topic}"

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/elsykes74-cpu/elvis-daily-script",
        "X-Title": "The King Lives - Elvis Daily Script",
    },
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    },
    timeout=60,
)

response.raise_for_status()
script = response.json()["choices"][0]["message"]["content"].strip()

word_count = len(script.split())
print(f"Script generated ({word_count} words)")
print(f"\n--- SCRIPT PREVIEW ---\n{script[:150]}...\n")

message = f"We are going to do an Elvis Presley video.\n\nSCRIPT:\n\n@quickkickbot {script}"

telegram_url = f"https://api.telegram.org/bot{LADYJAYE_BOT_TOKEN}/sendMessage"

telegram_response = requests.post(
    telegram_url,
    json={"chat_id": QUICKKICK_CHAT_ID, "text": message},
    timeout=30,
)

print(f"Telegram status: {telegram_response.status_code}")
if not telegram_response.ok:
    print(f"Telegram error body: {telegram_response.text}")
telegram_response.raise_for_status()
print("LadyJayeBot delivered script to QuickKick successfully")
print(f"Message ID: {telegram_response.json()['result']['message_id']}")
