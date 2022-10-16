import os.path
import re
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

project_id = "PROJECT_ID_HERE"
subscription_id = "default-sub"
topic_name = f'projects/{project_id}/topics/default'

log = logging.getLogger()


def setup_gmail_client():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def otp_message_to_be_present(gmail_client):

    def _predicate(driver):
        result = gmail_client.users().messages().list(userId='me', labelIds=['LABEL_ID_HERE', "UNREAD"],
                                                      maxResults=1, includeSpamTrash=False).execute()

        if 'messages' in result:
            message_id = result['messages'][0]['id']
            message = gmail_client.users().messages().get(userId='me', id=message_id, format='minimal').execute()
            log.info(f'OTP Message: {message}')
            message_received_mills = int(message['internalDate'])
            gmail_client.users().messages().modify(userId='me', id=message_id,
                                                   body={"removeLabelIds": ["UNREAD"]}).execute()
            if time.time() * 1000 - message_received_mills > 180000:
                log.error("OTP code expired.")
                return
            otp_code = re.search('[a-zA-Z]*[0-9]+[a-zA-Z]*', message['snippet']).group()

            return otp_code

    return _predicate
