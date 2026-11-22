from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


PROJECT_ROOT = Path(__file__).parent
credentials_file = PROJECT_ROOT / "credentials.json"
token_file = PROJECT_ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_credentials():
    """Метод авторизации в Google."""
    creds = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    token_file.write_text(creds.to_json())

    return creds


