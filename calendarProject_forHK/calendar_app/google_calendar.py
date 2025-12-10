import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
import datetime
from .calendar_service import CalendarService

# This file requires the following environment variables to be set:
# GOOGLE_CLIENT_ID: The client ID from your Google Cloud project.
# GOOGLE_CLIENT_SECRET: The client secret from your Google Cloud project.
# Make sure to add them to your .env file.

# The scope for the Google Calendar API.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# The URI to redirect to after the user grants/denies permission.
REDIRECT_URI = 'http://localhost:8000/oauth2callback'

class GoogleCalendarService(CalendarService):
    """
    An implementation of the CalendarService for Google Calendar.
    """

    def __init__(self):
        self.flow = self._get_flow()

    def _get_flow(self):
        """Initializes and returns a Flow object for the Google authentication process."""
        client_config = {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "project_id": "calendarproject-428909", #This can be a dummy value
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.token.uri.com/token", #This can be a dummy value
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", #This can be a dummy value
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [REDIRECT_URI],
            }
        }
        return google_auth_oauthlib.flow.Flow.from_client_config(
            client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )

    def get_authorization_url(self):
        """Generates and returns the Google authorization URL."""
        authorization_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state

    def fetch_token(self, authorization_response, state):
        """
        Fetches the OAuth 2.0 token from Google.
        """
        self.flow.state = state
        self.flow.fetch_token(authorization_response=authorization_response)
        return self.flow.credentials

    def list_events(self, credentials):
        """
        Lists the next 10 events on the user's primary calendar.
        """
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return events
