import requests
import datetime
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 定義したインターフェースとデータ型をインポート
from .weather_interface import IWeatherService, CandidateBatch

load_dotenv()

# ==========================================
# 設定: .envファイルからAPIキーを読み込みます
# ==========================================
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY_NAME = "Tokyo,JP"

# キーがない場合は自動的にTrueになります
USE_MOCK_DATA = True if not OPENWEATHER_API_KEY else False

class WeatherService:
    """
    OpenWeatherMapを使用した天気予報サービスの実装クラス
    IWeatherServiceインターフェースを継承しています
    """

    def filter_by_precipitation_30(self, datetime_ranges: List[List[datetime.datetime]]) -> List[List[datetime.datetime]]:

        """
        インターフェースの実装メソッド
        """
        # 1. APIから天気予報を取得 (またはモックデータ)
        ALLOWED_POP_PERCENT = 30
        
        forecast_list = self._fetch_forecast()
        
        valid_ranges: List[List[datetime.datetime]] = []

        # 2. 各候補日時について判定
        for time_range in datetime_ranges:
            start_time = time_range[0]
            end_time = time_range[1]
            
            # 最も近い予報データを探す
            target_forecast = self._find_closest_forecast(start_time, forecast_list)
            
            if target_forecast:
                # APIのpopは 0.0〜1.0 なので 100倍して％にする
                pop_percent = int(target_forecast.get('pop', 0) * 100)
                
                # デバッグ用: 必要に応じてコメントアウトを外してください
                # print(f"日時: {start_time} | 降水確率: {pop_percent}% (許容: {allowed_pop_percent}%)")

                if pop_percent <= ALLOWED_POP_PERCENT:
                    valid_ranges.append([start_time, end_time])
            else:
                # 予報データが見つからない場合（日付が遠すぎる、APIエラー等）は
                # 判定不能として、とりあえず候補に残す（安全側に倒す）
                valid_ranges.append([start_time, end_time])


        return valid_ranges

    def _fetch_forecast(self) -> List[Dict]:
        """
        OpenWeatherMap APIを叩く（またはモックを返す）内部メソッド
        """
        if USE_MOCK_DATA:
            # 開発中はログを出しておくと親切です
            # print("WeatherService: APIキーがないためモックデータを使用します")
            return self._get_mock_data()

        url = ("http://api.openweathermap.org/data/2.5/forecast"f"?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}")
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('list', [])
        except Exception as e:
            print(f"Weather API Error: {e}")
            # エラー時は空リストを返し、判定処理側で「予報なし」として扱う
            return []

    def _find_closest_forecast(self, target_dt: datetime.datetime, forecast_list: List[Dict]) -> Optional[Dict]:
        """
        ターゲット日時に最も近い予報データを探索する内部メソッド
        """
        closest_data = None
        min_diff = float('inf')

        # target_dtがタイムゾーン付きの場合はnaiveにする（簡易比較のため）
        if target_dt.tzinfo:
            target_dt = target_dt.replace(tzinfo=None)

        for item in forecast_list:
            # APIの時刻フォーマット: "2025-12-09 12:00:00"
            forecast_time_str = item.get('dt_txt')
            if not forecast_time_str:
                continue
                
            forecast_time = datetime.datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")
            
            # 差分（秒）を計算
            diff = abs((forecast_time - target_dt).total_seconds())
            
            # 3時間以内(10800秒)のデータで、かつ最も近いものを採用
            if diff < 10800 and diff < min_diff:
                min_diff = diff
                closest_data = item

        return closest_data

    def _get_mock_data(self) -> List[Dict]:
        """
        テスト用のダミー予報データを生成する内部メソッド
        """
        mock_list = []
        base_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # 向こう5日分、3時間ごとのデータを作る
        for i in range(40): # 5日 * 8回/日 = 40
            time_point = base_time + datetime.timedelta(hours=3 * i)
            
            # 偶数日は雨(100%)、奇数日は晴れ(0%)という単純なダミーロジック
            is_rainy = (time_point.day % 2 == 0) 
            pop = 1.0 if is_rainy else 0.0
            
            mock_list.append({
                "dt_txt": time_point.strftime("%Y-%m-%d %H:%M:%S"),
                "pop": pop, 
                "weather": [{"main": "Rain" if is_rainy else "Clear"}]
            })
        return mock_list