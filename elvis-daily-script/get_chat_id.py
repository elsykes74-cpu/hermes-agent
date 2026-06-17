"""
Helper script — run this LOCALLY to find QuickKick's chat_id.
Not needed in production. Safe to delete after setup.

Usage (Windows):
  set LADYJAYE_BOT_TOKEN=<your token here>
  python get_chat_id.py
"""
import os
import sys
import requests

token = os.environ.get("LADYJAYE_BOT_TOKEN", "").strip()
if not token:
    token = input("Enter LadyJayeBot token: ").strip()
if not token:
    print("ERROR: No token provided.")
    sys.exit(1)

print()
print("=" * 55)
print("STEP 1: Have QuickKick send a message to LadyJayeBot")
print("=" * 55)
print("  1. Open Telegram on your phone or desktop")
print("  2. Find @Quickkickbot")
print("  3. Have it send /start (or any message) to LadyJayeBot")
print()
input("Press Enter once QuickKick has messaged LadyJayeBot...")

url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"\nERROR calling getUpdates: {e}")
    print("Double-check your LADYJAYE_BOT_TOKEN and try again.")
    sys.exit(1)

updates = resp.json().get("result", [])

if not updates:
    print("\nNo updates found yet.")
    print("Make sure QuickKick sent a message to LadyJayeBot, then run this script again.")
    sys.exit(0)

print(f"\nFound {len(updates)} update(s). Showing unique chats:\n")
seen = set()
for update in updates:
    for key in ("message", "channel_post", "my_chat_member"):
        msg = update.get(key, {})
        if not msg:
            continue
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        if not chat_id or chat_id in seen:
            continue
        seen.add(chat_id)
        username = chat.get("username", "")
        name = chat.get("first_name") or chat.get("title") or ""
        chat_type = chat.get("type", "")
        print(f"  Chat ID  : {chat_id}")
        if username:
            print(f"  Username : @{username}")
        if name:
            print(f"  Name     : {name}")
        print(f"  Type     : {chat_type}")
        print()

print("=" * 55)
print("NEXT STEP")
print("=" * 55)
print("Copy the Chat ID for @Quickkickbot above.")
print()
print("Then go to:")
print("  GitHub -> your repo -> Settings -> Secrets and variables")
print("  -> Actions -> New repository secret")
print()
print("  Name : QUICKKICK_CHAT_ID")
print("  Value: <the chat ID from above>")
print()
print("After adding the secret, trigger the workflow manually:")
print("  Actions -> Elvis Daily Script -> Run workflow")
