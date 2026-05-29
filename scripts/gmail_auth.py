"""
Run this ONCE to get your Gmail refresh token.

    cd wbs-api
    python scripts/gmail_auth.py

Make sure your .env already has:
    GMAIL_CLIENT_ID=...
    GMAIL_CLIENT_SECRET=...

It will open a browser, you log in, then it prints your GMAIL_REFRESH_TOKEN.
Copy that into .env and you're done forever.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google_auth_oauthlib.flow import InstalledAppFlow
from core.config import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
    client_config = {
        "installed": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n✅ Add this to your .env:\n")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
