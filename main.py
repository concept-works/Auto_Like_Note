import csv
import time
import schedule
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ログファイルパス
CLICK_LOG_PATH = 'click_log.csv'
IP_LIST_PATH = 'ip_list.csv'

# 使用済みIPのインデックスをファイルで管理
def get_next_ip():
    with open(IP_LIST_PATH, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        ip_list = [row['ip'] for row in reader]

    if not ip_list:
        raise Exception("IPアドレスが見つかりません")

    try:
        with open('ip_index.txt', 'r') as f:
            index = int(f.read().strip())
    except FileNotFoundError:
        index = 0

    ip = ip_list[index]
    index = (index + 1) % len(ip_list)

    with open('ip_index.txt', 'w') as f:
        f.write(str(index))

    return ip

def has_been_clicked(url):
    try:
        with open(CLICK_LOG_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['url'] == url:
                    return True
    except FileNotFoundError:
        pass
    return False

def log_click(url, ip):
    with open(CLICK_LOG_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([url, datetime.now().isoformat(), ip])

def click_button(url, selector):
    if has_been_clicked(url):
        print(f"✅ 既にクリック済み：{url}")
        return

    ip = get_next_ip()
    print(f"🌐 使用IP：{ip} → {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"--proxy-server={ip}")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(5)
        button = driver.find_element("css selector", selector)
        button.click()
        print(f"✅ クリック成功：{url}")
        log_click(url, ip)
    except Exception as e:
        print(f"❌ エラー: {url} - {e}")
    finally:
        driver.quit()

def schedule_tasks():
    print("📋 タスク読み込み中...")
    tasks = pd.read_csv('tasks.csv')
    for _, row in tasks.iterrows():
        url = row["url"]
        selector = row["selector"]
        interval = int(row["interval"])
        unit = row["unit"]

        def job(u=url, s=selector):
            click_button(u, s)

        if unit == "時間":
            schedule.every(interval).hours.do(job)
        elif unit == "分":
            schedule.every(interval).minutes.do(job)
        elif unit == "日":
            schedule.every(interval).days.do(job)
        else:
            print(f"⚠️ 無効な単位: {unit}")

        print(f"📅 スケジュール設定: {url} - {interval} {unit}おき")

def run_scheduler():
    schedule_tasks()
    print("🚀 スケジューラー開始")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    print("📡 自動クリック開始！")
    run_scheduler()