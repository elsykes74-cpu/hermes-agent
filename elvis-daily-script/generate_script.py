import json
import os
import random
import datetime
import requests


def load_topics():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    topics_path = os.path.join(script_dir, "topics", "topics.json")
    with open(topics_path, "r") as f:
        return json.load(f)


def pick_topic(topics):
    seed = datetime.date.today().toordinal()
    rng = random.Random(seed)
    return rng.choice(topics)


def generate_script(topic, api_key):
    system_prompt = (
        "You are the head writer for The King Lives — a faceless Elvis Presley documentary YouTube channel. "
        "Write a single 60-second narration script about the assigned topic.\n\n"
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
    )

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": f"Today's topic: {topic}"}],
    }

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"].strip()


def send_telegram(bot_token, chat_id, script_text):
    message = f"We are going to do an Elvis Presley video.\n\nScript: {script_text}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    topics = load_topics()
    topic = pick_topic(topics)
    print(f"Topic: {topic}")

    script = generate_script(topic, api_key)
    word_count = len(script.split())
    print(f"Script generated ({word_count} words)")
    print("---")
    print(script)
    print("---")

    result = send_telegram(bot_token, chat_id, script)
    if result.get("ok"):
        print("Telegram message delivered successfully.")
    else:
        raise RuntimeError(f"Telegram delivery failed: {result}")


if __name__ == "__main__":
    main()
