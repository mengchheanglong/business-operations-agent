"""
One-time Google Sheets authentication script.
Run this once to generate a token.json file that the agent uses.
"""
import os
import sys
import json
from pathlib import Path

# Load .env
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value.strip())

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in .env")
        return

    # Create client config for installed app
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    print("=" * 60)
    print("  Google Sheets Authentication")
    print("=" * 60)
    print("\nA browser window will open. Sign in with your Google account")
    print("and grant permission to access Google Sheets.\n")

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token
    token_file = Path(__file__).parent.parent / "token.json"
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    token_file.write_text(json.dumps(token_data, indent=2))

    print(f"\n✅ Token saved to: {token_file}")
    print("The agent can now access Google Sheets!")

if __name__ == "__main__":
    main()
