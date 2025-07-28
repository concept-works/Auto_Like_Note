import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import schedule
import os
from datetime import datetime
import gspread
import random
from google.oauth2.service_account import Credentials

# ✅ ChromeDriverを自動インストール・対応バージョン確認
chromedriver_autoinstaller.install()

# ユーザーエージェントとリファラー生成
def generate_user_agent_and_referer():
    devices = ["SP", "PC"]
    sp_oses = ["Android", "iOS"]
    pc_oses = ["Windows", "macOS"]
    referers = [
        "https://twitter.com/",
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://note.com/",
        "https://www.instagram.com/",
        "https://www.facebook.com/",
        "https://jp.pinterest.com/",
        "https://www.tiktok.com/",
        "https://yahoo.co.jp/"
    ]

    device = random.choice(devices)

    if device == "SP":
        os_choice = random.choice(sp_oses)
        if os_choice == "Android":
            ua = "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36"
        else:
            ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
    else:
        os_choice = random.choice(pc_oses)
        if os_choice == "Windows":
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        else:
            ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"

    referer = random.choice(referers)
    return ua, referer

# IPアドレス管理
def get_next_ip():
    ip_path = os.path.join(os.path.dirname(__file__), 'ip_list.csv')
    index_path = os.path.join(os.path.dirname(__file__), 'ip_index.txt')

    df = pd.read_csv(ip_path)
    if df.empty or len(df) < 2:
        raise Exception("⚠️ IPリストに十分なデータがありません（最低2行必要）")

    total = len(df)
    current_index = 1

    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            try:
                current_index = int(f.read().strip())
            except:
                current_index = 1

    next_index = current_index + 1 if current_index + 1 < total else 1

    with open(index_path, 'w') as f:
        f.write(str(next_index))

    return df.iloc[current_index, 0]

# Google Sheets API認証
def get_gsheet_client():
    json_path = "/etc/secrets/credentials.json"
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(json_path, scopes=scopes)
    client = gspread.authorize(creds)
    return client

# Google Sheetsにログを記録
def log_click_to_sheet(url, ip="60.69.77.243", user_agent="", referer=""):
    try:
        print("🔗 Google Sheets にログ記録中...", flush=True)
        client = get_gsheet_client()
        sheet = client.open("Auto_Like_Note").worksheet("log")

        now = datetime.now().isoformat()
        sheet.append_row([url, now, ip, user_agent, referer])
        print(f"📝 Sheets記録完了: {url}, {now}, {ip}, {user_agent}, {referer}", flush=True)

    except Exception as e:
        print(f"⚠️ Sheetsログ保存エラー: {e}", flush=True)

# クリック処理
def click_element(url, selector):
    print(f"▶️ click_element実行: {url} / {selector}", flush=True)
    try:
        ip_address = get_next_ip()
        user_agent, referer = generate_user_agent_and_referer()
        print(f"🧭 使用UA: {user_agent}", flush=True)
        print(f"🔁 リファラー: {referer}", flush=True)

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={user_agent}")

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {"Referer": referer}
        })

        driver.get(url)
        time.sleep(3)

        element = driver.find_element("css selector", selector)
        element.click()
        print("✅ クリック成功", flush=True)
        driver.quit()

        log_click_to_sheet(url, ip=ip_address, user_agent=user_agent, referer=referer)

    except Exception as e:
        print(f"❌ クリック失敗: {e}", flush=True)

# スケジューリング処理
def schedule_tasks():
    print("📋 タスクスケジュール設定開始", flush=True)
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'tasks.csv')
        print(f"📄 CSVパス: {csv_path}", flush=True)

        df = pd.read_csv(csv_path)
        print("✅ CSV読み込み成功", flush=True)

        for index, row in df.iterrows():
            try:
                url = row["url"]
                selector = row["selector"]
                interval = int(row["interval"])
                unit = row["unit"]

                print(f"📝 タスク{index + 1}: {url}, {selector}, {interval}, {unit}", flush=True)

                click_element(url, selector)

                if unit == "分":
                    schedule.every(interval).minutes.do(click_element, url, selector)
                elif unit == "時間":
                    schedule.every(interval).hours.do(click_element, url, selector)
                elif unit == "日":
                    schedule.every(interval).days.do(click_element, url, selector)
                else:
                    print(f"⚠️ 未対応の単位: {unit}", flush=True)

            except Exception as e:
                print(f"❌ タスク設定失敗（{index + 1}行目）: {e}", flush=True)

    except Exception as e:
        print(f"❌ タスクスケジュール設定エラー: {e}", flush=True)
        exit(1)

# スケジューラー起動
def run_scheduler():
    print("⏱️ スケジューラー起動", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)

# メイン処理
if __name__ == "__main__":
    print("🚀 main.py 起動", flush=True)
    schedule_tasks()
    print("📡 自動クリック開始！ Ctrl+C で終了します", flush=True)
    run_scheduler()