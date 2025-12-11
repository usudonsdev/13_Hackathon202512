from django.db.models import Q
#TODO: ↑のフォルダ構成に合わせて修正
from typing import List
from .friend_interface import IFriendService
from ..models import Friend  # モデル名はUser定義に合わせて適宜修正してください

class FriendService(IFriendService):
    """
    フレンド機能の実装クラス
    accept status: 0=申請中, 1=承認済み
    """
    
    STATUS_PENDING = 0
    STATUS_ACCEPTED = 1

    def get_friend_list(self, user_id) -> List[str]:
        """
        [追加] ユーザーのフレンドID一覧を取得する
        ご提示のSQLロジック（UNION）を実装
        """
        uid = str(user_id)  #userテーブルのidの文字列変換型をuidとする

        # SQL: select user2 FROM Friend where user1 = uid AND accept = 1
        # 自分が user1 側のとき、フレンドは user2
        qs1 = Friend.objects.filter(
            user1=uid, 
            accept=self.STATUS_ACCEPTED
        ).values_list('user2', flat=True)

        # SQL: select user1 FROM Friend where user2 = uid AND accept = 1
        # 自分が user2 側のとき、フレンドは user1
        qs2 = Friend.objects.filter(
            user2=uid, 
            accept=self.STATUS_ACCEPTED
        ).values_list('user1', flat=True)

        # UNION で結合してリスト化
        # union() はDjangoの機能でSQLのUNIONを発行します
        friend_ids = qs1.union(qs2)
        
        return list(friend_ids) #Listにして返す

    def is_friend(self, user_id1, user_id2) -> bool:
        """
        フレンド判定
        高速化のため、一覧取得ではなく直接検索(exists)を使用
        """
        u1 = str(user_id1)
        u2 = str(user_id2)

        return Friend.objects.filter(
            (Q(user1=u1) & Q(user2=u2)) | (Q(user1=u2) & Q(user2=u1)),
            accept=self.STATUS_ACCEPTED
        ).exists()

    def create_request(self, from_user_id, to_user_id) -> bool:
        u1 = str(from_user_id)
        u2 = str(to_user_id)
        if u1 == u2: return False

        exists = Friend.objects.filter(
            (Q(user1=u1) & Q(user2=u2)) | (Q(user1=u2) & Q(user2=u1))
        ).exists()

        if exists: return False

        Friend.objects.create(
            user1=u1,
            user2=u2,
            accept=self.STATUS_PENDING
        )
        return True

    def accept_request(self, from_user_id, to_user_id) -> bool:
        try:
            # 申請者(user1) -> 自分(user2) のリクエストを探す
            req = Friend.objects.get(
                user1=str(from_user_id),
                user2=str(to_user_id),
                accept=self.STATUS_PENDING
            )
            req.accept = self.STATUS_ACCEPTED
            req.save()
            return True
        except Friend.DoesNotExist:
            return False

    def delete_friend(self, user_id1, user_id2) -> bool:
        u1 = str(user_id1)
        u2 = str(user_id2)
        count, _ = Friend.objects.filter(
            (Q(user1=u1) & Q(user2=u2)) | (Q(user1=u2) & Q(user2=u1))
        ).delete()
        return count > 0