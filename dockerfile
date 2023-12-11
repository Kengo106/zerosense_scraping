# Pythonの公式イメージをベースに使用
FROM python:3

# 作業ディレクトリの設定
WORKDIR /usr/src/app

# 必要なPythonライブラリのインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ChromeとChromeDriverのインストール
RUN apt-get update && apt-get install -y \
    unzip \
    wget \
    vim \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
ADD https://chromedriver.storage.googleapis.com/93.0.4577.15/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && unzip chromedriver_linux64.zip && chmod +x chromedriver
ENV PATH $PATH:/opt/chrome

# アプリケーションのファイルをコンテナにコピー 
#最初の . はホストマシンの現在のディレクトリを指し、二番目の . はコンテナ内の作業ディレクトリ（WORKDIR で定義されたディレクトリ）を指す
COPY . . 

CMD ["/bin/bash"]
