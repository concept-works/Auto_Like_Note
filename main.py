import pandas as pd
import random
import time
import schedule
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

csv_file = "tasks.csv"
if not os.path.exists(csv_file):
    print("❌ tasks.csv が見つかりません。")
    exit()

df = pd.read_csv(csv_file)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36"
]

domestic_ips = [
    "133.242.100.100", "157.112.145.1", "150.95.55.10", "153.127.202.50"
]

def perform_action(url, selector):
    ua = random.choice(user_agents)
    ip = random.choice(domestic_ips)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={ua}")

    driver = webdriver.Chrome(options=options)

    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {"X-Forwarded-For": ip}
        })
    except Exception as e:
        print(f"⚠ ヘッダ設定エラー: {e}")

    try:
        driver.get(url)
        time.sleep(2)
        driver.find_element("css selector", selector).click()
        print(f"✅ クリック成功: {url} の {selector}")
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        driver.quit()

def schedule_task(row):
    url = row['access_url']
    selector = row['click_selector']
    interval = int(row['interval'])
    unit = row['unit'].strip()

    base_minutes = interval * 60 if unit == "時間" else interval * 1440
    jitter = random.randint(-10, 10)
    total_minutes = max(1, base_minutes + jitter)

    def task():
        perform_action(url, selector)

    schedule.every(total_minutes).minutes.do(task)
    print(f"🔁 {total_minutes}分ごとに {url} をクリック")

for _, row in df.iterrows():
    schedule_task(row)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

print("📡 自動クリック開始！ Ctrl+C で終了します")
run_scheduler()