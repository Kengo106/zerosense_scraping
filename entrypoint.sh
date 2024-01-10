#!/bin/bash

# 環境変数DJANGO_DEBUGをチェック
echo "$HOST"
if [ "$LOCAL" = "True" ]; then
    開発用コマンド
    echo 'debug=true'
    cd zerosense
    python manage.py runserver 0.0.0.0:$PORT
    # cd zerosense
    # ls
    # gunicorn -b :$PORT zerosense.wsgi
else
    # 本番用コマンド
    echo 'debug=false'
    cd zerosense
    ls
    gunicorn -b :$PORT -t 500 zerosense.wsgi
fi
 