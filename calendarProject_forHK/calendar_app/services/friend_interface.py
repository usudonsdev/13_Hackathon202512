from abc import ABC, abstractmethod
from typing import List, Union

# IDは文字列(ユーザー名)の場合も数値の場合もあるため、両方許容する型定義
UserID = Union[str, int]

class IFriendService(ABC):
    """
    フレンド機能のビジネスロジックを定義するインターフェース
    """

    @abstractmethod
    def is_friend(self, user_id1: UserID, user_id2: UserID) -> bool:
        """
        2人がフレンド関係（承認済み）かどうか判定する
        """
        pass

    @abstractmethod
    def get_friend_list(self, user_id: UserID) -> List[str]:
        """
        指定したユーザーのフレンドID一覧を取得する
        """
        pass

    @abstractmethod
    def create_request(self, from_user_id: UserID, to_user_id: UserID) -> bool:
        """
        フレンド申請を作成する
        from_user -> to_user
        """
        pass

    @abstractmethod
    def accept_request(self, from_user_id: UserID, to_user_id: UserID) -> bool:
        """
        フレンド申請を承認する
        from_user: 申請を送ってきた人
        to_user: 自分（承認する人）
        """
        pass

    @abstractmethod
    def delete_friend(self, user_id1: UserID, user_id2: UserID) -> bool:
        """
        フレンド関係（または申請）を削除・解除する
        """
        pass