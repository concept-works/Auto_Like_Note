#!/usr/bin/env bash

# システム更新と必要なパッケージのインストール
apt-get update
apt-get install -y wget unzip curl gnupg

# Chromeのインストール
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Pythonの依存関係をインストール
pip install -r requirements.txt