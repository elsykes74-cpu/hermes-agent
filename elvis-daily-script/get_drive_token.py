"""
Run this ONCE on your machine to get your Google Drive refresh token.

Prerequisites:
    pip install google-auth-oauthlib

Steps:
    1. Run: python get_drive_token.py
    2. Paste your Client ID and Client Secret when prompted
    3. Browser opens — sign in as elsykes74@gmail.com and click Allow
    4. Copy the three values printed at the end into GitHub Secrets
"""
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_ID = input("Paste your Google OAuth Client ID: ").strip()
CLIENT_SECRET = input("Paste your Google OAuth Client Secret: ").strip()

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    },
    scopes=["https://www.googleapis.com/auth/drive"],
)
creds = flow.run_local_server(port=0)

print("\n" + "=" * 60)
print("ADD THESE THREE VALUES TO GITHUB SECRETS:")
print("=" * 60)
print(f"GOOGLE_CLIENT_ID     = {CLIENT_ID}")
print(f"GOOGLE_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"GOOGLE_REFRESH_TOKEN = {creds.refresh_token}")
print("=" * 60)
