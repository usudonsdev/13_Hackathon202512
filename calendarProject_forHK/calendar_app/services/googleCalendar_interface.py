from abc import ABC, abstractmethod
from typing import Tuple, Any, List

class CalendarService(ABC):
    """
    Googleカレンダー等のカレンダーサービスの抽象基底クラス（インターフェース）
    """

    @abstractmethod
    def get_authorization_url(self) -> Tuple[str, str]:
        """
        認証URLを取得する。
        
        Returns:
            Tuple[str, str]: (authorization_url, state) のタプル
        """
        pass

    @abstractmethod
    def fetch_token(self, authorization_response: str, state: str) -> Any:
        """
        OAuth 2.0 トークンを取得する。
        
        Args:
            authorization_response (str): コールバックURL全体
            state (str): 状態文字列
            
        Returns:
            Any: 認証情報 (Credentialsオブジェクトなど)
        """
        pass

    @abstractmethod
    def list_events(self, credentials: Any) -> List[Any]:
        """
        カレンダーのイベントリストを取得する。
        
        Args:
            credentials (Any): fetch_tokenで取得した認証情報
            
        Returns:
            List[Any]: イベントオブジェクトのリスト
        """
        pass