この構成は、**フロントとバックエンドの連携エラー（CORSや認証周り）が起きにくく、ハッカソンでは非常に堅実で賢い選択**です。

それに伴い、役割と作成ファイルを再定義しました。「HTMLをサーバーから返す部分」と「動きをつけるJS部分」の切り分けがポイントになります。

---

# スマートスケジューラー 実装担当割（Django Template版）

## アーキテクチャ変更点

- **画面描画:** DjangoがHTMLを生成して返します（Server Side Rendering）。
- **動的処理:** 予定のドラッグ＆ドロップやAI提案の読み込みだけ、`fetch` (AJAX) を使って非同期で行います。

---

## 👨‍💻 1人目：フロントエンド（HTML/CSS/JS）

**ミッション:** Djangoテンプレートを使った画面構築と、素のJSによるDOM操作。

### 作成すべきファイルと仕様

### 1. `templates/base.html` (共通レイアウト)

- **内容:** ヘッダー、フッター、CSS/JSの読み込み定義。
- **I/O:**
    - **Input:** `{% block content %}`
    - **Output:** 全ページの骨格となるHTML。

### 2. `templates/scheduler/calendar.html` (メイン画面)

- **内容:** メインのカレンダー画面。Djangoのテンプレートタグ `{% for %}` を使って、初期表示時点の予定を描画する。
- **I/O:**
    - **Input (Context):** `{{ events }}` (バックエンドから渡された予定リスト)
    - **Structure:** CSS Gridを使って30分刻みの枠を作る。HTML
        
        `<div class="time-slot" data-time="10:00"></div>`
        

### 3. `static/js/calendar.js` (カレンダーの動き)

- **内容:** 予定クリック時のモーダル表示や、AI提案ボタンを押したときの非同期通信。
- **I/O:**
    - **Input:** DOM要素（ボタン、予定ブロック）
    - **Process:**
        - AI提案ボタン押下 → `fetch('/api/recommend/', ...)` を実行。
        - 返ってきたJSONを見て、画面上に「提案ブロック」を動的に`createElement`で追加する。

### 4. `templates/scheduler/modal_form.html` (インクルード用)

- **内容:** `<dialog>` タグなどを使った予定入力フォーム。
- **I/O:**
    - **Input:** フォーム送信時、`action="{% url 'event_create' %}"` へPOSTする（標準的なForm送信）。

---

## 👨‍💻 2人目：スケジュール管理機能 & Docker

**ミッション:** 「画面を表示するためのView」と「JSONを返すAPI View」の両方を作る必要があります。

### 作成すべきファイルと仕様

### 1. `scheduler/forms.py` (Django Form)

- **内容:** 予定入力フォームの定義。HTMLバリデーションを楽にするため。
- **I/O:** `Event` モデルをベースにした `ModelForm`。

### 2. `scheduler/views.py` (画面表示 & フォーム処理)

- **内容:** テンプレートを表示するメインの処理。
- **I/O:**
    - **GET /calendar/**
        - `events = Event.objects.filter(user=request.user)`
        - `return render(request, 'scheduler/calendar.html', {'events': events})`
    - **POST /event/new/**
        - フォームを受け取り保存 → `return redirect('calendar')` (画面遷移する)

### 3. `scheduler/api_views.py` (AJAX用 JSON API)

- **内容:** フロントのJSから呼ばれる「小回り」の効くAPI。
- **I/O:**
    - **POST /api/event/update/** (ドラッグ移動時など)
        - Input: `{ id: 1, new_start: "..." }`
        - Output: `{ status: "ok" }` JSON

### 4. `Dockerfile` / `docker-compose.yml`

- **変更点:** フロントエンドのビルドプロセス（Node.jsコンテナ）が不要になるため、構成がシンプルになります。Pythonコンテナ1つでOKです。

---

## 👨‍💻 3人目：データ設計 & ソーシャル機能 & UI補助

**ミッション:** モデル設計は変わらず。ソーシャル機能は「専用ページ」を作る形になります。

### 作成すべきファイルと仕様

### 1. `scheduler/models.py` (★最重要)

- **内容:** 変更なし。`User`, `Event`, `Friendship`, `BaseLifeTask` を定義。

### 2. `templates/scheduler/friend_list.html`

- **内容:** 友達一覧と、友達検索フォーム。
- **I/O:**
    - **Input (Context):** `{{ friends }}`
    - **Output:** 友達リストのHTML。各友達に「カレンダーを見る」リンクを貼る。

### 3. `scheduler/views_social.py`

- **内容:** 友達の予定を見るためのView。
- **I/O:**
    - **GET /friends/[int:friend_id](https://www.google.com/search?q=int:friend_id)/calendar/**
        - 指定されたIDのユーザーの予定を取得（`privacy='PUBLIC'` でフィルタリング）。
        - `render(request, 'scheduler/calendar.html', {'events': friend_events, 'is_friend_view': True})`
        - ※自分のカレンダーと同じテンプレートを使い回すと効率が良い。

---

## 👨‍💻 4人目：AI & スマート提案機能

**ミッション:** ロジックはPython側にあるため、フレームワーク変更の影響をほぼ受けません。JSから呼ばれるAPIを作ります。

### 作成すべきファイルと仕様

### 1. `scheduler/services/recommendation.py` (ロジック)

- **内容:** 変更なし。空き時間を計算してリストで返すPython関数。

### 2. `scheduler/views_ai.py` (提案API)

- **内容:** JSの `fetch` から叩かれるエンドポイント。
- **I/O:**
    - **POST /api/recommend/**
        - Input (JSON): `{ "duration": 60, "condition": "..." }`
        - Output (JSON):JSON
            
            `{
              "candidates": [
                {"start": "2025-12-08T10:00", "end": "...", "score": 90},
                {"start": "2025-12-08T14:00", "end": "...", "score": 80}
              ]
            }`
            
        - **注意:** ここは `render` ではなく `JsonResponse` を返します。

### 3. `static/js/recommendation.js` (フロント連携)

- **内容:** 1人目のJSファイルが大きくなりすぎないよう、AI関連のJS処理（ボタンを押して候補を表示し、クリックしたらフォームに入れる処理）を担当。

---

## 💡 開発フローの変更点まとめ

1. **データ通信:** 基本は「画面遷移（リロード）」です。
2. **API:** 「すべてをAPIにする」のではなく、「AI提案」や「非同期更新」のような**部分的な機能だけ**をAPI化（`JsonResponse`）します。
3. **結合:**
    - 1人目（HTML）と2人目（View）の密な連携が必要です。「テンプレートに渡す変数名（`{{ events }}` なのか `{{ schedule_list }}` なのか）」を最初に決めておくとスムーズです。

この体制であれば、Reactの学習コストゼロで、Djangoの知識だけで完結できます。実装頑張ってください！
