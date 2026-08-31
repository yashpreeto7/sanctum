"""Google OAuth 2.0 Setup Utility for Gmail and Google Calendar.

This script guides you through authenticating with Google Cloud to grant Personal AI OS
access to read/send emails and manage calendar events.
"""

from pathlib import Path
import sys

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth Scopes for Personal AI OS
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / ".tmp" / "google_token.json"


def authenticate_google_oauth(credentials_path: Path = CREDENTIALS_FILE, token_path: Path = TOKEN_FILE):
    """Runs the OAuth 2.0 InstalledAppFlow browser authentication flow."""
    token_path.parent.mkdir(parents=True, exist_ok=True)
    creds = None

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired Google OAuth token...")
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print(f"❌ Error: '{credentials_path.name}' not found at:\n   {credentials_path}")
                print("\nPlease follow these steps:")
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("2. Create a project and enable 'Gmail API' and 'Google Calendar API'")
                print("3. Configure OAuth Consent Screen (User Type: External, add your email as Test User)")
                print("4. Create OAuth Client ID credentials (Application Type: Desktop App)")
                print("5. Download the JSON file and rename it to 'credentials.json' in your project root.")
                return False

            print("🌐 Launching local browser for Google OAuth authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
        print(f"✅ Authentication successful! Token saved to:\n   {token_path}")

    return creds


if __name__ == "__main__":
    success = authenticate_google_oauth()
    if success:
        print("\n🎉 Google Workspace OAuth setup is complete. Personal AI OS can now interact with live Gmail and Calendar.")
    else:
        sys.exit(1)
