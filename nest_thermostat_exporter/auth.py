# Copyright 2020 Thomas Helander
# All rights reserved.
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/sdm.service"]
API_SERVICE_NAME = "smartdevicemanagement"
API_VERSION = "v1"

CREDENTIALS_FILE = os.path.join(
    os.path.expanduser("~"), ".nest-metrics-credentials.json"
)


def get_authenticated_service(client_secret_path):
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes=SCOPES,)

    if not os.path.exists(CREDENTIALS_FILE):
        credentials = flow.run_console()
        Path(CREDENTIALS_FILE).touch(mode=0o600)
        with open(CREDENTIALS_FILE, "w") as fp:
            fp.write(credentials.to_json())
    else:
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE)

    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Should only be one enterprise, so return it.
    return service.enterprises()
