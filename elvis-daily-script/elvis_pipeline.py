#!/usr/bin/env python3
"""
Elvis Full Pipeline — concept to YouTube in one run.

Steps:
  1. Pick today's topic (date-seeded, same logic as Apps Script)
  2. Generate narration script via OpenRouter (130-150 words)
  3. Generate 7-scene breakdown
  4. Generate voiceover MP3 via ElevenLabs
  5. Generate 7 scene images via Ideogram 4
  6. Assemble 9:16 MP4 with FFmpeg
  7. Upload to YouTube (private by default)

Usage:
  python elvis_pipeline.py
  python elvis_pipeline.py --publish          # go public immediately
  python elvis_pipeline.py --dry-run          # stop before video gen + upload
  python elvis_pipeline.py --auth-youtube     # one-time YouTube OAuth login

Required env vars (copy .env.example to .env and fill in):
  OPENROUTER_API_KEY
  ELEVENLABS_API_KEY
  ELEVENLABS_VOICE_ID
  IDEOGRAM_API_KEY
  YOUTUBE_CLIENT_SECRETS_FILE
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
TOOLKIT_TOOLS = SCRIPT_DIR / "video-toolkit" / "tools"
TOPICS_FILE = SCRIPT_DIR / "topics" / "topics.json"
OUT_DIR = SCRIPT_DIR / "output"

sys.path.insert(0, str(TOOLKIT_TOOLS))

# ── Config ────────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")
IDEOGRAM_API_KEY = os.environ.get("IDEOGRAM_API_KEY", "")
YOUTUBE_CLIENT_SECRETS = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-sonnet-4-6"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/elsykes74-cpu/hermes-agent",
    "X-Title": "The King Lives - Elvis Daily Script",
}

# ElevenLabs settings from production notes
ELEVENLABS_SETTINGS = {
    "stability": 0.70,
    "similarity_boost": 0.65,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 0.88,
}

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


# ── Step 1: Topic selection ───────────────────────────────────────────────────

def pick_topic() -> tuple[str, str]:
    """Return (date_str, topic) seeded by today's date."""
    today = datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")
    seed = sum(ord(c) for c in date_str)
    topics = json.loads(TOPICS_FILE.read_text())
    topic = topics[seed % len(topics)]
    return date_str, topic


# ── Step 2: Script generation ─────────────────────────────────────────────────

def generate_script(topic: str) -> str:
    resp = requests.post(
        OPENROUTER_URL,
        headers=OPENROUTER_HEADERS,
        json={
            "model": OPENROUTER_MODEL,
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
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Step 3: Scene breakdown ───────────────────────────────────────────────────

def generate_scene_breakdown(script: str) -> str:
    resp = requests.post(
        OPENROUTER_URL,
        headers=OPENROUTER_HEADERS,
        json={
            "model": OPENROUTER_MODEL,
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a documentary video editor. Break the script into exactly 7 scenes.\n\n"
                        "STRICT RULES:\n"
                        "- Exactly 7 scenes\n"
                        "- Timestamps start at 00:00 and end at 01:00 exactly\n"
                        "- Visual direction is one concrete sentence for Ideogram image generation\n"
                        "- Style: black and white vintage documentary photography, cinematic\n"
                        "- Do not invent content — only use words from the script\n"
                        "- Output ONLY this exact format:\n\n"
                        "Scene 1 | 00:00 - 00:08\n"
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
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Scene parser ──────────────────────────────────────────────────────────────

def parse_scenes(breakdown: str) -> list[dict]:
    """Parse scene breakdown into list of {start, end, duration, visual_direction}."""
    scenes = []
    pattern = re.compile(
        r"Scene \d+ \| (\d{2}:\d{2}) - (\d{2}:\d{2})\n.*?\nVisual direction: (.+)",
        re.DOTALL,
    )
    for m in pattern.finditer(breakdown):
        start = _ts_to_sec(m.group(1))
        end = _ts_to_sec(m.group(2))
        scenes.append({
            "start": start,
            "end": end,
            "duration": end - start,
            "visual_direction": m.group(3).strip(),
        })
    return scenes


def _ts_to_sec(ts: str) -> float:
    parts = ts.split(":")
    return int(parts[0]) * 60 + int(parts[1])


# ── Step 4: Voiceover ─────────────────────────────────────────────────────────

def generate_voiceover(script: str, output_path: Path) -> Path:
    """Call ElevenLabs API directly with production settings."""
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    if not ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID not set")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": ELEVENLABS_SETTINGS,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    print(f"  Voiceover: {output_path} ({len(resp.content) // 1024}KB)")
    return output_path


# ── Step 5: Scene images ──────────────────────────────────────────────────────

def generate_scene_image(visual_direction: str, output_path: Path, scene_num: int) -> Path:
    """Generate one image via Ideogram 4 API."""
    if not IDEOGRAM_API_KEY:
        raise RuntimeError("IDEOGRAM_API_KEY not set")

    prompt = (
        f"{visual_direction} "
        "Style: black and white vintage documentary photography, 1950s-1970s, "
        "cinematic, high contrast, grain, Memphis Tennessee, Elvis Presley era. "
        "No text, no watermarks, portrait orientation."
    )

    resp = requests.post(
        "https://api.ideogram.ai/v1/ideogram-v4/generate",
        headers={
            "Api-Key": IDEOGRAM_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "image_request": {
                "prompt": prompt,
                "resolution": "1080x1920",
                "rendering_speed": "TURBO",
                "num_images": 1,
                "style_type": "REALISTIC",
            }
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    image_url = data["data"][0]["url"]

    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    output_path.write_bytes(img_resp.content)
    print(f"  Scene {scene_num} image: {output_path.name}")
    return output_path


# ── Step 6: FFmpeg assembly ───────────────────────────────────────────────────

def assemble_video(scenes: list[dict], image_paths: list[Path],
                   audio_path: Path, output_path: Path) -> Path:
    """Stitch scene images + voiceover into a 9:16 MP4 using FFmpeg."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False, dir=OUT_DIR) as f:
        concat_file = Path(f.name)
        for i, (scene, img) in enumerate(zip(scenes, image_paths)):
            f.write(f"file '{img.resolve()}'\n")
            f.write(f"duration {scene['duration']}\n")
        # FFmpeg concat demuxer requires repeating last file
        f.write(f"file '{image_paths[-1].resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path),
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
               f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    concat_file.unlink(missing_ok=True)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError("FFmpeg failed")
    print(f"  Video assembled: {output_path}")
    return output_path


# ── Step 7: YouTube upload ────────────────────────────────────────────────────

def upload_to_youtube(video_path: Path, topic: str, script: str,
                      date_str: str, publish: bool) -> str:
    """Upload via the toolkit's youtube_upload.py."""
    title = f"The King Lives — {topic[:80]}"
    privacy = "public" if publish else "private"

    description = (
        f"The King Lives | {date_str}\n\n"
        f"{script}\n\n"
        "─────────────────────────────\n"
        "The King Lives is a daily faceless documentary channel about Elvis Presley.\n"
        "New video every morning.\n\n"
        "#ElvisPresley #TheKingLives #ElvisDocumentary #Elvis #Documentary"
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False, dir=OUT_DIR) as f:
        desc_file = Path(f.name)
        f.write(description)

    uploader = str(TOOLKIT_TOOLS / "youtube_upload.py")
    cmd = [
        sys.executable, uploader,
        "--video", str(video_path),
        "--title", title,
        "--description-file", str(desc_file),
        "--tags", "Elvis Presley,Elvis,The King Lives,documentary,history,music history",
        "--privacy", privacy,
        "--client-secrets", YOUTUBE_CLIENT_SECRETS,
        "--json-out",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    desc_file.unlink(missing_ok=True)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError("YouTube upload failed")

    out = json.loads(result.stdout)
    video_id = out.get("id", "unknown")
    url = f"https://youtu.be/{video_id}"
    print(f"  YouTube: {url} ({privacy})")
    return url


# ── Main ──────────────────────────────────────────────────────────────────────

def check_deps():
    missing = []
    if not OPENROUTER_API_KEY:
        missing.append("OPENROUTER_API_KEY")
    if not ELEVENLABS_API_KEY:
        missing.append("ELEVENLABS_API_KEY")
    if not ELEVENLABS_VOICE_ID:
        missing.append("ELEVENLABS_VOICE_ID")
    if not IDEOGRAM_API_KEY:
        missing.append("IDEOGRAM_API_KEY")
    if not YOUTUBE_CLIENT_SECRETS:
        missing.append("YOUTUBE_CLIENT_SECRETS_FILE")
    elif not Path(YOUTUBE_CLIENT_SECRETS).exists():
        missing.append(f"YOUTUBE_CLIENT_SECRETS_FILE (file not found: {YOUTUBE_CLIENT_SECRETS})")
    if subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0:
        missing.append("ffmpeg (not installed — brew install ffmpeg or apt install ffmpeg)")
    return missing


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--publish", action="store_true",
                    help="Upload as public (default: private)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Generate script only, skip images/video/upload")
    ap.add_argument("--auth-youtube", action="store_true",
                    help="Run one-time YouTube OAuth browser login")
    args = ap.parse_args()

    # One-time YouTube auth
    if args.auth_youtube:
        uploader = str(TOOLKIT_TOOLS / "youtube_upload.py")
        subprocess.run([sys.executable, uploader, "--auth",
                        "--client-secrets", YOUTUBE_CLIENT_SECRETS], check=True)
        return

    # Dependency check
    missing = check_deps()
    if missing:
        print("Missing required configuration:")
        for m in missing:
            print(f"  - {m}")
        print("\nCopy elvis-daily-script/.env.example to elvis-daily-script/.env and fill it in.")
        sys.exit(1)

    OUT_DIR.mkdir(exist_ok=True)

    # ── 1. Topic
    date_str, topic = pick_topic()
    print(f"\nThe King Lives — {date_str}")
    print(f"Topic: {topic}\n")

    # ── 2. Script
    print("Generating script...")
    script = generate_script(topic)
    word_count = len(script.split())
    print(f"  {word_count} words")

    # ── 3. Scene breakdown
    print("Generating scene breakdown...")
    breakdown = generate_scene_breakdown(script)
    scenes = parse_scenes(breakdown)
    print(f"  {len(scenes)} scenes parsed")

    if args.dry_run:
        print("\n--- SCRIPT ---")
        print(script)
        print("\n--- SCENES ---")
        print(breakdown)
        print("\n[dry-run] Stopping before image generation.")
        return

    run_dir = OUT_DIR / date_str
    run_dir.mkdir(exist_ok=True)

    # ── 4. Voiceover
    print("Generating voiceover (ElevenLabs)...")
    audio_path = generate_voiceover(script, run_dir / "voiceover.mp3")

    # ── 5. Scene images
    print("Generating scene images (Ideogram 4)...")
    image_paths = []
    for i, scene in enumerate(scenes, 1):
        img_path = run_dir / f"scene_{i:02d}.jpg"
        generate_scene_image(scene["visual_direction"], img_path, i)
        image_paths.append(img_path)

    # ── 6. Assemble video
    print("Assembling video (FFmpeg)...")
    video_path = run_dir / f"{date_str}_Elvis.mp4"
    assemble_video(scenes, image_paths, audio_path, video_path)

    # ── 7. Upload
    print("Uploading to YouTube...")
    url = upload_to_youtube(video_path, topic, script, date_str, args.publish)

    print(f"\nDone. {url}")
    print(f"Files saved to: {run_dir}")


if __name__ == "__main__":
    main()
