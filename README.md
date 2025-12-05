# 環境構築


## 目次


### 1. 必要なソフト、拡張機能のインストール
### 2. 仕上げ



## 1. 必要なソフト、拡張機能のインストール


##### その1 `Docker Desktop`
    
    https://www.docker.com/products/docker-desktop/

ここに飛んでWindows用のインストーラをダウンロードしてきたらあとはインストーラ指示に従うだけ

##### その2 `git Desktop`
    
    https://gitforwindows.org/

ここに飛んでインストーラをダウンロードしてきたらあとはインストーラ指示に従うだけ,,,なはず

##### その3 vscodeの拡張機能たち



##　2. 仕上げ


##### 1. コマンド実行手順

メンバーは以下のコマンドを順番に打つだけで環境が完成します。

**リポジトリをコピー（クローン）する**

    1. リポジトリを入れたいフォルダでターミナル、コマンドプロンプト等を開く
    2. `git clone https://github.com/usudonsdev/13_Hackathon202512.git` と実行する 
    3. `cd 13_Hackathon202512` でカレントディレクトリがプロジェクトフォルダになる


**Dockerコンテナをビルド＆起動する**
    
これが「環境構築」の全てです。このコマンドだけでPythonのインストールからライブラリの準備まで全自動で行われます。

    docker-compose up -d --build


**参考までに**
    `up`        : 起動
    `-d`        : バックグラウンドで実行
    `--build`   : 最初にイメージを作成するために必要


**データベースのセットアップ（マイグレーション）**

コンテナが立ち上がったら、データベースの初期設定を行います。

    docker-compose exec web python manage.py migrate


**動作確認**

ブラウザで http://localhost:8000 にアクセスして、ロケットの画面（またはアプリの画面）が出れば成功です！


# ここからセットアップ完了後にやること


**Dockerコンテナをビルド＆起動する**
    
Webサイトを起動したいときはこのコマンドを実行すればOK

    docker-compose up -d --build



## Gitを使う際の注意事項

**⚠️ 開発中の注意点（ここが重要！）**

共同開発中、誰かが「新しいライブラリ（例：カレンダー操作用ライブラリ）」を追加した時は、以下のルールを守ってください。



**ライブラリを入れた人**
    
`pip install` だけでなく、必ず `requirements.txt` を更新してGitに上げる。


**コンテナ内で freeze して書き出す例**

    docker-compose exec web pip freeze > requirements.txt

その後に 
    
    git add requirements.txt / git commit / git push

を実行


**他のメンバー**

`git pull` で `requirements.txt` が更新されていたら、必ずビルドし直す。

    git pull
    docker-compose up -d --build  # <-- これをやらないと新しいライブラリが入らずエラーになる




##　入れた方がいい拡張機能

**indent-rainbow:**インデントの色分け
**TODOs:**TODOって書いてコメントアウトすると後で一覧で確認できるから、やり残しとかを書いておくとよい
**GitLens':**Gitのブランチを俯瞰できる。全員の進捗が一目でわかる
**GeminiCodeAssistant:**Geminiのコーディング版　フォルダを丸ごと読んでコメントしてくれる　有能
(Windsurf)


##### あとがき

https://zenn.dev/headwaters/articles/0ff2e65239546d

このリンクを参考に環境構築しました


TODO    データベースの構築手順
TODO    ブランチの切り方、マージのルール