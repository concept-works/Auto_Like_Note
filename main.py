import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import schedule
import os
import random
from datetime import datetime

# --- IPアドレス取得 ---
def get_next_ip(ip_file='ip_list.csv', index_file='ip_index.txt'):
    ip_df = pd.read_csv(ip_file)
    ip_list = ip_df['ip'].tolist()

    if len(ip_list) < 1:
        raise ValueError("IPリストが空です")

    max_index = len(ip_list) - 1

    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            index = int(f.read().strip())
    else:
        index = 0

    selected_ip = ip_list[index]
    new_index = index + 1 if index + 1 <= max_index else 0

    with open(index_file, 'w') as f:
        f.write(str(new_index))

    return selected_ip

# --- User-Agentのランダム生成 ---
def get_random_user_agent():
    devices = ["PC", "Smartphone"]
    browsers = ["Chrome", "Firefox", "Safari"]
    pc_os = ["Windows NT 10.0", "Macintosh; Intel Mac OS X 10_15_7"]
    sp_os = ["iPhone; CPU iPhone OS 14_0 like Mac OS X", "Linux; Android 10"]

    device = random.choice(devices)
    browser = random.choice(browsers)

    if device == "PC":
        os_part = random.choice(pc_os)
        ua_device = ""
    else:
        os_part = random.choice(sp_os)
        ua_device = "Mobile "

    if browser == "Chrome":
        browser_part = "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    elif browser == "Firefox":
        browser_part = "Gecko/20100101 Firefox/89.0"
    else:
        browser_part = "Version/14.0 Mobile/15E148 Safari/604.1"

    user_agent = f"Mozilla/5.0 ({os_part}) {ua_device}{browser_part}"
    return user_agent

# --- ログ記録 ---
def log_click(url, ip):
    log_path = os.path.join(os.path.dirname(__file__), 'click_log.csv')
    now = datetime.now().isoformat()
    try:
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write("url,click,ip\n")
        with open(log_path, 'a') as f:
            f.write(f"{url},{now},{ip}\n")
        print(f"📝 クリックログ記録: {url}, {now}, {ip}", flush=True)
    except Exception as e:
        print(f"⚠️ クリックログ保存エラー: {e}", flush=True)

# --- 実行処理 ---
def click_element(url, selector):
    ip = get_next_ip()
    user_agent = get_random_user_agent()
    print(f"▶️ click_element実行: {url} / {selector} / IP: {ip} / UA: {user_agent}", flush=True)

    try:
        options = Options()
        # 可視モード（ヘッドレスにしない）
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--proxy-server={ip}")  # IPアドレス

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        element = driver.find_element("css selector", selector)
        element.click()
        print("✅ クリック成功", flush=True)
        driver.quit()

        log_click(url, ip)

    except Exception as e:
        print(f"❌ クリック失敗: {e}", flush=True)

# --- スケジュール読み込み ---
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

# --- スケジューラー実行 ---
def run_scheduler():
    print("⏱️ スケジューラー起動", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- 実行エントリーポイント ---
if __name__ == "__main__":
    print("🚀 main.py 起動", flush=True)
    schedule_tasks()
    print("📡 自動クリック開始！ Ctrl+C で終了します", flush=True)
    run_scheduler()