#!/usr/bin/env bash
# エラーが出たらそこで止まるようにする設定
set -o errexit

# 正しいフォルダに移動
cd calendarProject_forHK

# データベースの更新
python manage.py migrate

# サーバーの起動
gunicorn calendarProject_forHK.wsgi:application --bind 0.0.0.0:10000