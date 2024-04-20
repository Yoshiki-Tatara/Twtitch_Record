import os
import subprocess
import time
import logging
import requests

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 環境変数から設定を読み込む
CHANNEL_NAME = os.getenv('TWITCH_CHANNEL_NAME')
RECORD_PATH = os.getenv('RECORD_PATH')
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
AUTHORIZATION_TOKEN = os.getenv('TWITCH_AUTHORIZATION_TOKEN')

if not CHANNEL_NAME or not RECORD_PATH or not CLIENT_ID or not AUTHORIZATION_TOKEN:
    logging.error('環境変数が設定されていません。')
    exit(1)

# 必要なモジュールのインポート
try:
    import schedule
except ImportError:
    logging.error('scheduleモジュールが見つかりません。インストールしてください。')
    exit(1)

# 配信が生放送中かどうかを確認する関数
def is_live(channel):
    url = f"https://api.twitch.tv/helix/streams?user_login={channel}"
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {AUTHORIZATION_TOKEN}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # ステータスコードが200以外の場合にエラーを発生させる
        data = response.json()
        return data['data'] != []  # データが空でなければ生放送中
    except requests.RequestException as e:
        logging.error(f'APIリクエスト中にエラーが発生しました: {e}')
        return False

# 配信の録画を開始する関数
def record_stream(channel):
    if is_live(channel):
        logging.info(f"{channel} is live! Starting recording...")
        command = f"streamlink --output {RECORD_PATH}{channel}.ts twitch.tv/{channel} best"
        try:
            subprocess.check_call(command, shell=True)
            logging.info(f"録画が正常に開始されました: {channel}")
        except subprocess.CalledProcessError as e:
            logging.error(f"録画の開始に失敗しました: {e}")
    else:
        logging.info(f"{channel} is not live.")

# 定期的に配信をチェックするジョブをスケジュール
schedule.every(10).minutes.do(record_stream, CHANNEL_NAME)

# 無限ループでジョブを実行
while True:
    schedule.run_pending()
    time.sleep(1)
