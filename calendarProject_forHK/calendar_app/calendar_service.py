from abc import ABC, abstractmethod

class CalendarService(ABC):
    """
    An interface for a calendar service.
    """

    @abstractmethod
    def get_authorization_url(self):
        """
        Generates and returns the authorization URL for the calendar service.
        Should return a tuple of (authorization_url, state).
        """
        pass

    @abstractmethod
    def fetch_token(self, authorization_response, state):
        """
        Fetches the OAuth 2.0 token from the calendar service.
        Should return the credentials.
        """
        pass

    @abstractmethod
    def list_events(self, credentials):
        """
        Lists events from the calendar service.
        Should return a list of events.
        """
        pass
