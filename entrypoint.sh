#!/bin/bash

# 環境変数DEBUGが設定されているかチェック
if [ "$DJANGO_DEBUG" = "true" ]; then
    # 開発用コマンド
    echo 'debug=true'
    cd zerosense
    python manage.py runserver 0.0.0.0:8000
else
    # 本番用コマンド
    echo 'debug=false'
    gunicorn -b :$PORT zerosense.wsgi
fi
 