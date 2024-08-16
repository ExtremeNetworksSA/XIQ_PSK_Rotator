import os
import inspect
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
import logging
from app.logger import logger
logger = logging.getLogger('PSK_Rotator.google_api')
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

class new():
    __version__ = "0.0.1"
    __author__  = "Tim Smith (tismith@extremenetworks.com)"

    #################################################################################################
    def __init__(self, yml_variables):
        self.yml_variables = yml_variables
        self.SCOPES = ['https://mail.google.com/']

         # get the Gmail API service
        self.service = self._gmail_authenticate()


    def _gmail_authenticate(self):
        creds = None
        # the file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
        if os.path.exists(f"{parent_dir}/token.pickle"):
            with open(f"{parent_dir}/token.pickle", "rb") as token:
                creds = pickle.load(token)
        # if there are no (valid) credentials availablle, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(f'{parent_dir}/credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # save the credentials for the next run
            with open(f"{parent_dir}/token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds, cache_discovery=False)

   
    def build_message(self, recipients, obj, body):
        message = MIMEText(body)
        message['to'] = ', '.join(recipients)
        message['subject'] = obj
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}   

    def send_message(self, body, attachments=[]):
        return self.service.users().messages().send(
          userId="me",
          body=self.build_message(self.yml_variables['email_list'], self.yml_variables['email_sub'], body)
        ).execute()
