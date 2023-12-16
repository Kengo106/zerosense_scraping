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
    libfontconfig1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 
# Google Chromeのダウンロードと展開
ADD https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/linux64/chrome-linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip

# ChromeDriverのダウンロードと展開
ADD https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/linux64/chromedriver-linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chromedriver-linux64.zip && \
    chmod +x -R chromedriver-linux64 && \
    rm chromedriver-linux64.zip

# Chrome Headless Shellのダウンロードと展開
ADD https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/linux64/chrome-headless-shell-linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chrome-headless-shell-linux64.zip && \
    rm chrome-headless-shell-linux64.zip

ENV PATH $PATH:/opt/chrome

# アプリケーションのファイルをコンテナにコピー 
# 最初の . はホストマシンの現在のディレクトリを指し、二番目の . はコンテナ内の作業ディレクトリ（WORKDIR で定義されたディレクトリ）を指す
COPY . . 

CMD ["/bin/bash"]
