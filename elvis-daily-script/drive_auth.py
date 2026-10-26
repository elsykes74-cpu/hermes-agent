#!/usr/bin/env python3
"""
One-time Google Drive OAuth setup for The King Lives pipeline.

Usage:
  python drive_auth.py --client-secrets /path/to/client_secret_123.json

What it does:
  1. Prints an authorization URL
  2. You visit it in any browser and authorize access to Google Drive
  3. You paste the code back into the terminal
  4. Saves a refresh token to .credentials/drive_token.json

After running this once, the pipeline uploads to Drive automatically.

Getting client_secret_*.json (2 minutes):
  1. Go to console.cloud.google.com
  2. Create or select a project
  3. APIs & Services → Enable APIs → search "Google Drive API" → Enable
  4. APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
  5. Application type: Desktop app → Create → Download JSON
  6. Run: python drive_auth.py --client-secrets ~/Downloads/client_secret_*.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDS_DIR = Path(__file__).parent / ".credentials"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--client-secrets", metavar="PATH",
                    default=os.environ.get("GOOGLE_DRIVE_CLIENT_SECRETS_FILE", ""),
                    help="Path to client_secret_*.json from Google Cloud Console")
    args = ap.parse_args()

    if not args.client_secrets:
        ap.error("Pass --client-secrets or set GOOGLE_DRIVE_CLIENT_SECRETS_FILE in .env")

    secrets_path = Path(args.client_secrets)
    if not secrets_path.exists():
        ap.error(f"File not found: {secrets_path}")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        ap.error("Run: pip install google-auth-oauthlib")

    CREDS_DIR.mkdir(exist_ok=True)
    token_file = CREDS_DIR / "drive_token.json"

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)

    print("\nStarting Google Drive authorization...")
    print("This will open a URL for you to authorize access.\n")

    creds = flow.run_console()

    token_file.write_text(creds.to_json())
    print(f"\nToken saved to: {token_file}")
    print("\nSetup complete — the pipeline can now upload to Google Drive automatically.")

    # Write the client secrets path to .env if not already there
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        content = env_file.read_text()
        if "GOOGLE_DRIVE_CLIENT_SECRETS_FILE=" in content:
            lines = []
            for line in content.splitlines():
                if line.startswith("GOOGLE_DRIVE_CLIENT_SECRETS_FILE="):
                    lines.append(f"GOOGLE_DRIVE_CLIENT_SECRETS_FILE={secrets_path.resolve()}")
                else:
                    lines.append(line)
            env_file.write_text("\n".join(lines) + "\n")
        else:
            with env_file.open("a") as f:
                f.write(f"\nGOOGLE_DRIVE_CLIENT_SECRETS_FILE={secrets_path.resolve()}\n")
        print(f"Updated .env with GOOGLE_DRIVE_CLIENT_SECRETS_FILE")


if __name__ == "__main__":
    main()
