import datetime
# ★ここを scheduler から calendar_app に修正しました
from calendar_app.services.weather import WeatherService
from calendar_app.services.weather_interface import CandidateBatch

def run_demo():
    print("=== 天気フィルタリング デモ開始 ===")

    # 1. サービスのインスタンス化
    weather_service = WeatherService()

    # 2. テストデータの準備（明日以降のデータを生成）
    base_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    
    candidates = []
    for i in range(5):
        start_dt = base_time + datetime.timedelta(days=i)
        start_dt = start_dt.replace(hour=12)
        end_dt = start_dt + datetime.timedelta(hours=1)
        candidates.append({'start': start_dt, 'end': end_dt})
    
    print(f"判定前の候補数: {len(candidates)}件")
    for c in candidates:
        print(f" - {c['start'].strftime('%Y-%m-%d %H:%M')}")

    # 3. データをBatchオブジェクトにまとめる
    batch = CandidateBatch(candidates)

    # 4. フィルタリング実行 (降水確率 20% 以下のみ許可)
    print("\n--- フィルタリング実行 (許容降水確率: 20%以下) ---")
    filtered_results = weather_service.filter_by_precipitation(batch, allowed_pop_percent=20)

    # 5. 結果表示
    print(f"\n判定後の候補数: {len(filtered_results)}件")
    print("--- 通過した日時リスト ---")
    for res in filtered_results:
        print(f" [OK] {res['start'].strftime('%Y-%m-%d %H:%M')}")
    print("\n=== デモ終了 ===")

if __name__ == "__main__":
    run_demo()