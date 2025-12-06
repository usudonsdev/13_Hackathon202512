```mermaid
usecaseDiagram
    actor "ユーザー" as User
    actor "登録フレンド" as Friend
    actor "Googleカレンダー" as GCal
    actor "天気API" as Weather
    actor "LLM (AI)" as LLM

    package "スマートスケジューラー" {
        usecase "予定を登録する\n(通常・ルーティン)" as AddEvent
        usecase "自然言語で予定入力" as NLPInput
        usecase "予定を削除する\n(警告あり)" as DeleteEvent
        
        usecase "最適日時を提案してもらう\n(期間・天気・所要時間)" as GetRecommendation
        usecase "空き時間を可視化する" as VisualizeGaps
        
        usecase "フレンドの予定を確認する\n(Publicのみ)" as ViewFriend
        usecase "複数人でスケジュール調整" as MultiSched
        
        usecase "GCal同期 (一方通行)" as SyncGCal
    }

    User --> AddEvent
    User --> NLPInput
    User --> DeleteEvent
    User --> GetRecommendation
    User --> VisualizeGaps
    User --> MultiSched
    User --> ViewFriend

    NLPInput ..> LLM : 解析依頼
    GetRecommendation ..> Weather : 天気情報取得
    GetRecommendation ..> LLM : 提案ロジック
    SyncGCal ..> GCal : インポート

```