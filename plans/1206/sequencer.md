sequenceDiagram
    autonumber
    actor User
    participant Frontend as UI/Frontend
    participant Logic as Backend/Scheduler
    participant DB as Database
    participant Weather as WeatherAPI
    participant LLM as LLM/AI

    User->>Frontend: 「2週間以内で美容室に行きたい(2時間)」と入力
    Frontend->>Logic: 条件送信(期間:14日, 所要時間:120分, text="美容室")
    
    par 並列処理
        Logic->>DB: ユーザーの既存予定・基礎生活時間を取得
        DB-->>Logic: 予定リスト返却
    and
        Logic->>Weather: 向こう2週間の天気予報を取得
        Weather-->>Logic: 天気データ(雨の日特定)
    end

    Logic->>Logic: 30分単位で空きスロットを計算
    Logic->>Logic: 雨の日を除外フィルタリング

    opt 自然言語解析が必要な場合
        Logic->>LLM: 文脈から追加制約を抽出
        LLM-->>Logic: 制約条件(例: 美容室なら昼間が良い等)
    end

    Logic->>Logic: 候補リストを作成(Top 3)
    Logic-->>Frontend: 提案日時リストを表示
    
    Frontend->>User: 候補を表示(A: 明後日10:00, B: 土曜14:00...)
    User->>Frontend: 候補Bを選択
    Frontend->>Logic: 予定確定リクエスト
    Logic->>DB: Event保存
    Logic-->>Frontend: 登録完了
    Frontend-->>User: カレンダーに反映