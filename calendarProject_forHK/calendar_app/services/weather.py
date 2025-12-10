import requests
import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 設定: .envファイルからAPIキーを読み込みます
# ==========================================
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")

#TODO 都市を選択できるようにする
CITY_NAME = "Tokyo,JP"

USE_MOCK_DATA = True   # APIキーがない場合は True にするとダミーデータで動きます

class CandidateBatch:
    """
    候補日時のリストをまとめるオブジェクト
    """
    def __init__(self, candidates: List[Dict[str, datetime.datetime]]):
        # candidatesの形式例: 
        # [{'start': datetime(...), 'end': datetime(...)}, ...]
        self.candidates = candidates

class WeatherService:
    @staticmethod
    def filter_by_precipitation(candidate_batch: CandidateBatch, allowed_pop_percent: int) -> List[Dict[str, datetime.datetime]]:
        
        """
        候補日時のうち、降水確率が許容値以下のものだけを返すメソッド

        Args:
            candidate_batch (CandidateBatch): 候補日時のリストを含むオブジェクト
            allowed_pop_percent (int): 許容する降水確率 (0-100)

        Returns:
            List[Dict]: 条件をクリアした候補日時のリスト
        """
        
        # 1. APIから天気予報を取得 (またはモックデータ)
        forecast_list = WeatherService._fetch_forecast()
        
        valid_candidates = []

        # 2. 各候補日時について判定
        for candidate in candidate_batch.candidates:
            start_time = candidate['start']
            
            # 最も近い予報データを探す
            target_forecast = WeatherService._find_closest_forecast(start_time, forecast_list)
            
            if target_forecast:
                # APIのpopは 0.0〜1.0 なので 100倍して％にする
                pop_percent = int(target_forecast.get('pop', 0) * 100)
                
                print(f"日時: {start_time} | 降水確率: {pop_percent}% (許容: {allowed_pop_percent}%)")

                if pop_percent <= allowed_pop_percent:
                    valid_candidates.append(candidate)
            else:
                # 予報データが見つからない場合（日付が遠すぎる等）はとりあえず通す
                # TODO 本当にこれでいいか？
                valid_candidates.append(candidate)

        return valid_candidates

    @staticmethod
    def _fetch_forecast():
        """OpenWeatherMap APIを叩く（またはモックを返す）"""
        if USE_MOCK_DATA:
            return WeatherService._get_mock_data()

        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('list', [])
        except Exception as e:
            print(f"Weather API Error: {e}")
            return []

    @staticmethod
    def _find_closest_forecast(target_dt: datetime.datetime, forecast_list: List[Dict]) -> Dict:
        """ターゲット日時に最も近い予報データを探索する"""
        closest_data = None
        min_diff = float('inf')

        # target_dtがタイムゾーン付きの場合はnaiveにする（簡易比較のため）
        if target_dt.tzinfo:
            target_dt = target_dt.replace(tzinfo=None)

        for item in forecast_list:
            # dt_txt形式: "2025-12-09 12:00:00"
            forecast_time_str = item.get('dt_txt')
            forecast_time = datetime.datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")
            
            # 差分（秒）を計算
            diff = abs((forecast_time - target_dt).total_seconds())
            
            # 3時間以内(10800秒)のデータで、かつ最も近いものを採用
            if diff < 10800 and diff < min_diff:
                min_diff = diff
                closest_data = item

        return closest_data

    @staticmethod
    def _get_mock_data():
        """テスト用のダミー予報データを生成"""
        mock_list = []
        base_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # 向こう5日分、3時間ごとのデータを作る
        for i in range(40): # 5日 * 8回/日 = 40
            time_point = base_time + datetime.timedelta(hours=3 * i)
            
            # 偶数日は雨(100%)、奇数日は晴れ(0%)という単純なダミー
            is_rainy = (time_point.day % 2 == 0) 
            pop = 1.0 if is_rainy else 0.0
            
            mock_list.append({
                "dt_txt": time_point.strftime("%Y-%m-%d %H:%M:%S"),
                "pop": pop, # Probability of Precipitation
                "weather": [{"main": "Rain" if is_rainy else "Clear"}]
            })
        return mock_list