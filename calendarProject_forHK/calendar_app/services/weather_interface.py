from abc import ABC, abstractmethod
from typing import List, Dict
import datetime

# データの型定義（Type Hinting用）
# 辞書の中身が何なのかを明確にします
class CandidateDict(Dict):
    start: datetime.datetime
    end: datetime.datetime

class CandidateBatch:
    """
    候補日時のリストをまとめるオブジェクト
    （データ構造のみを定義）
    """
    def __init__(self, candidates: List[Dict[str, datetime.datetime]]):
        self.candidates = candidates

class IWeatherService(ABC):
    """
    天気予報サービスのインターフェース
    """
    
    @abstractmethod
    def filter_by_precipitation(self, candidate_batch: CandidateBatch, allowed_pop_percent: int) -> List[Dict[str, datetime.datetime]]:
        """
        候補日時のうち、降水確率が許容値以下のものだけを返す
        
        Args:
            candidate_batch: 候補日時のリスト
            allowed_pop_percent: 許容する降水確率(0-100)
            
        Returns:
            条件を満たす候補日時のリスト
        """
        pass