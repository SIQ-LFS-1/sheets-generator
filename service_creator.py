import os
import pickle
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials


def Create_Service(client_secret_file, api_name, api_version, *scopes):
    # print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    # print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    # looking for pickle file
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        # print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to create service...')
        print(e)
        return None

# create service with a service account file...


def Create_Service2(key_file_location, api_name, api_version, scopes):
    try:
        """ creates a service object to communicate with Google Drive API via a service account.
        key_file_location: The path to a valid service account JSON key file.
        Returns the service object
        """

        credentials = service_account.Credentials.from_service_account_file(
            key_file_location)

        scoped_creds = credentials.with_scopes(scopes)

        # Build the service object
        service = build(api_name, api_version, credentials=scoped_creds)

        return service

    except Exception as error:
        print("Error in Service_Creator.py ::: ", error)
        return None


def gspreadService(service_secret_file):
    # Authorize using the credentials file
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_secret_file, scope)
    return (gspread.authorize(credentials))
