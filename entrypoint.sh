#!/bin/bash

# 環境変数DJANGO_DEBUGをチェック
if [ "$DJANGO_DEBUG" = "True" ]; then
    # 開発用コマンド
    echo 'debug=true'
    cd zerosense
    python manage.py runserver 0.0.0.0:8000
else
    # 本番用コマンド
    echo 'debug=false'
    cd zerosense
    ls
    gunicorn -b :$PORT zerosense.wsgi
fi
 