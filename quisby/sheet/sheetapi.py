from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import sys

from quisby import custom_logger

home_dir = os.getenv("HOME")
CONFIG_DIR = home_dir + '/.quisby/config/'
TOKEN_FILE = CONFIG_DIR + 'token.json'
OAUTH_CLIENT_FILE = CONFIG_DIR + 'oauth_credentials.json'  # Downloaded from Google Cloud Console
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'


def check_google_credentials_exist():
    if not os.path.exists(OAUTH_CLIENT_FILE):
        custom_logger.error("OAuth credentials not found at " + CONFIG_DIR)
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        sys.exit(1)


check_google_credentials_exist()

creds = None

# If token already exists, load it
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

# If no valid creds, do the OAuth flow
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CLIENT_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save credentials for next run
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

# Build the Sheets service
service = build("sheets", "v4", credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)
sheet = service.spreadsheets()
