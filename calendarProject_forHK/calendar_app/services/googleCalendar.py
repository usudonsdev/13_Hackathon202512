import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
import datetime
from .googleCalendar_interface import CalendarService

from datetime import timezone


# This file requires the following environment variables to be set:
# GOOGLE_CLIENT_ID: The client ID from your Google Cloud project.
# GOOGLE_CLIENT_SECRET: The client secret from your Google Cloud project.
# Make sure to add them to your .env file.

# Google Calendar APIがユーザーのデータのどこまで触っていいかを決める(今回はcalendarの読み込みのみ)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# ユーザーがGoogleの画面で「許可」ボタンを押した後に、戻ってくる先のURLです
REDIRECT_URI = 'http://localhost:8000/oauth2callback'


#TODO googleカレンダーへの書き込みの実装
#TODO 実際のURLで認証が通るかのテストは統合テスト時に実行
class GoogleCalendarService(CalendarService):
    """
    An implementation of the CalendarService for Google Calendar.
    """
    
    #コンストラクタ(_get_flow()を呼び出す)
    def __init__(self):
        self.flow = self._get_flow()

    #Googleと通信するための設定（Flowオブジェクト）を作る
    def _get_flow(self):
        """Initializes and returns a Flow object for the Google authentication process."""
        #ここにはGoogle Cloud Platformで発行された「身分証明書」のような情報をセット
        client_config = {
            "web": {
                #TODO auth_uri, token_uriはダミーなので、本番時は修正
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
        now = datetime.now(timezone.utc).isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return events


""" 

list_events()の実装例:

    取得したイベントに対して,

    for event in events:
        # タイトルの取得（なければ "No Title"）
        summary = event.get('summary', 'No Title')
    
        # 開始時刻の取得（dateTimeがなければdateを見る）
        start = event.get('start')
        start_time = start.get('dateTime', start.get('date'))
    
        print(f"{start_time}: {summary}")
"""