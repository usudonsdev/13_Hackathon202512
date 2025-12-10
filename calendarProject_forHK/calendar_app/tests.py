from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .calendar_service import CalendarService
# 修正箇所: UserとPlanのインポート元を分けます
from django.contrib.auth.models import User  # Userはここからインポート
from .models import Plan                     # Planはここからインポート
from datetime import datetime, timezone

class MockCalendarService(CalendarService):
    """
    A mock implementation of the CalendarService for testing.
    """
    def get_authorization_url(self):
        return "http://mock-auth-url.com", "mock_state"

    def fetch_token(self, authorization_response, state):
        creds = MagicMock()
        creds.to_json.return_value = '{"token": "mock_token"}'
        return creds

    def list_events(self, credentials):
        return [
            {
                'summary': 'Test Event 1',
                'description': 'This is a test event.',
                'start': {'dateTime': '2025-12-25T10:00:00+09:00'},
                'end': {'dateTime': '2025-12-25T11:00:00+09:00'},
            },
            {
                'summary': 'Test Event 2',
                'description': 'Another test event.',
                'start': {'dateTime': '2025-12-26T14:00:00+09:00'},
                'end': {'dateTime': '2025-12-26T15:30:00+09:00'},
            },
        ]

class TestGoogleCalendarIntegration(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    @patch('calendar_app.views.GoogleCalendarService', new=MockCalendarService)
    def test_google_calendar_auth_callback(self):
        """
        Tests the google_calendar_auth_callback view with a mock service.
        """
        # Setup session with the mock state
        session = self.client.session
        session['oauth_state'] = 'mock_state'
        session.save()

        # Make a GET request to the callback URL
        response = self.client.get(reverse('calendar_app:google_calendar_auth_callback'), {'state': 'mock_state'})

        # Check that the user is redirected to the index page
        self.assertRedirects(response, reverse('calendar_app:index'))

        # Check that the Plan objects were created in the database
        self.assertEqual(Plan.objects.count(), 2)

        # Check the details of the created plans
        plan1 = Plan.objects.get(name='Test Event 1')
        self.assertEqual(plan1.user, str(self.user))
        self.assertEqual(plan1.memo, 'This is a test event.')
        self.assertEqual(plan1.start_datetime, datetime.fromisoformat('2025-12-25T10:00:00+09:00'))
        self.assertEqual(plan1.end_datetime, datetime.fromisoformat('2025-12-25T11:00:00+09:00'))

        plan2 = Plan.objects.get(name='Test Event 2')
        self.assertEqual(plan2.user, str(self.user))
        self.assertEqual(plan2.memo, 'Another test event.')
        self.assertEqual(plan2.start_datetime, datetime.fromisoformat('2025-12-26T14:00:00+09:00'))
        self.assertEqual(plan2.end_datetime, datetime.fromisoformat('2025-12-26T15:30:00+09:00'))

# You can run this test by running one of the following commands in your terminal:
# python manage.py test calendar_app
# python manage.py test calendar_app.tests.TestGoogleCalendarIntegration
# python manage.py test calendar_app.tests.TestGoogleCalendarIntegration.test_google_calendar_auth_callback