import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import schedule
import os
from datetime import datetime

def get_next_ip(ip_file, index_file):
    ip_df = pd.read_csv(ip_file)
    ip_list = ip_df['ip'].tolist()

    if len(ip_list) < 1:
        raise ValueError("IPリストが空です")

    # 0行目はヘッダー、2行目が index 0 として扱う
    max_index = len(ip_list) - 1

    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            index = int(f.read().strip())
    else:
        index = 0

    # 次のIP取得
    selected_ip = ip_list[index]
    new_index = index + 1 if index + 1 <= max_index else 0

    with open(index_file, 'w') as f:
        f.write(str(new_index))

    return selected_ip

def log_click(url, ip, log_file):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{url},{now},{ip}\n")

def click_element(url, selector, ip, log_file):
    print(f"▶️ click_element実行: {url} / {selector} / IP: {ip}", flush=True)
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--proxy-server={ip}")  # IPアドレスを使用

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        element = driver.find_element("css selector", selector)
        element.click()
        print("✅ クリック成功", flush=True)
        driver.quit()

        log_click(url, ip, log_file)

    except Exception as e:
        print(f"❌ クリック失敗: {e}", flush=True)

def schedule_tasks():
    print("📋 タスクスケジュール設定開始", flush=True)

    task_file = os.path.join(os.path.dirname(__file__), 'task.csv')
    ip_file = os.path.join(os.path.dirname(__file__), 'ip_list.csv')
    index_file = os.path.join(os.path.dirname(__file__), 'ip_index.txt')
    log_file = os.path.join(os.path.dirname(__file__), 'click_log.csv')

    df = pd.read_csv(task_file)

    for index, row in df.iterrows():
        url = row["url"]
        selector = row["selector"]
        interval = int(row["interval"])
        unit = row["unit"]

        print(f"📝 タスク{index + 1}: {url}, {selector}, {interval}, {unit}", flush=True)

        ip = get_next_ip(ip_file, index_file)
        click_element(url, selector, ip, log_file)

        if unit == "分":
            schedule.every(interval).minutes.do(lambda u=url, s=selector: click_element(u, s, get_next_ip(ip_file, index_file), log_file))
        elif unit == "時間":
            schedule.every(interval).hours.do(lambda u=url, s=selector: click_element(u, s, get_next_ip(ip_file, index_file), log_file))
        elif unit == "日":
            schedule.every(interval).days.do(lambda u=url, s=selector: click_element(u, s, get_next_ip(ip_file, index_file), log_file))
        else:
            print(f"⚠️ 未対応の単位: {unit}", flush=True)

def run_scheduler():
    print("⏱️ スケジューラー起動", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 main.py 起動", flush=True)
    schedule_tasks()
    print("📡 自動クリック開始！ Ctrl+C で終了します", flush=True)
    run_scheduler()