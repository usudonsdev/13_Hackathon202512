import datetime
import re
from typing import Optional, Dict, Any, Tuple

# インターフェースがあれば継承、なければ単独クラスとして定義
try:
    from .llm_interface import ILLMService
    BaseClass = ILLMService
except ImportError:
    BaseClass = object

class RuleBasedService(BaseClass):
    """
    AIを使わず、正規表現で日時を抽出するパーサー
    """

    def parse_event_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        テキストから日時とタイトルを抽出する
        対応パターン例:
        - "明日の10時から会議"
        - "12/25 18:00 クリスマスパーティー"
        - "来週火曜 13:00 ランチ"
        """
        now = datetime.datetime.now()
        
        # 1. 日付の抽出
        target_date, text_without_date = self._extract_date(text, now)
        
        # 2. 時刻の抽出
        start_time, end_time, text_final = self._extract_time(text_without_date, target_date)
        
        # 3. 残った文字をタイトルとする
        title = text_final.strip()
        # 接続詞などを削除
        title = re.sub(r'^(から|の|で|に)\s*', '', title)
        
        if not title:
            title = "（タイトルなし）"

        # 4. JSONデータの構築
        return {
            "title": title,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "description": "自動解析により作成",
            "location": ""
        }

    def _extract_date(self, text: str, base_date: datetime.datetime) -> Tuple[datetime.datetime, str]:
        """日付キーワードを認識してdatetimeと、除去後のテキストを返す"""
        target_date = base_date

        # パターンA: 相対日 (明日, 明後日)
        if '明日' in text:
            target_date += datetime.timedelta(days=1)
            text = text.replace('明日', '')
        elif '明後日' in text:
            target_date += datetime.timedelta(days=2)
            text = text.replace('明後日', '')
        elif '今日' in text:
            text = text.replace('今日', '')
        
        # パターンB: 日付指定 (12/25, 12月25日)
        date_match = re.search(r'(\d{1,2})[/月](\d{1,2})日?', text)
        if date_match:
            month, day = map(int, date_match.groups())
            # 年またぎ処理（現在12月で、1月の日付が来たら来年とする）
            year = base_date.year
            if base_date.month == 12 and month == 1:
                year += 1
            
            target_date = target_date.replace(year=year, month=month, day=day)
            text = text.replace(date_match.group(0), '')

        return target_date, text

    def _extract_time(self, text: str, target_date: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime, str]:
        """時刻を抽出して開始・終了時間を返す"""
        # デフォルト: 翌日の10:00〜11:00
        start_dt = target_date.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # パターン: 18:00, 18時30分, 9時
        time_match = re.search(r'(\d{1,2})[:時](\d{0,2})', text)
        
        if time_match:
            hour = int(time_match.group(1))
            minute_str = time_match.group(2)
            minute = int(minute_str) if minute_str else 0
            
            # 午後補正（入力が "2時" でも "14時" の可能性が高いが、簡易的にそのまま採用）
            start_dt = target_date.replace(hour=hour, minute=minute, second=0)
            text = text.replace(time_match.group(0), '')
            
            # 「分」などの残骸を消す
            text = text.replace('分', '')

        # 終了時間（デフォルトで1時間後）
        end_dt = start_dt + datetime.timedelta(hours=1)

        return start_dt, end_dt, text
    

#TODO   正規表現の受付はこれだけでよいのか
#TODO   そもそもこれで動くのか
#TODO   日時分の融合形式にも対応したい