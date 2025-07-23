import csv
import random
import time
from datetime import datetime, timedelta
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === 国内IPアドレスのサンプル ===
DOMESTIC_IPS = [
    "133.106.32.1", "123.45.67.89", "202.32.14.10", "219.99.5.11", "106.73.12.8"
]

# === ユーザーエージェントの候補 ===
USER_AGENTS = [
    # PC系
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    # スマホ系
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36"
]

# === ヘッドレスChromeのドライバ生成 ===
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.binary_location = "/usr/bin/google-chrome"
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(options=options)

# === タスクの実行処理 ===
def execute_task(url, selector):
    print(f"[{datetime.now()}] アクセス開始: {url}")
    driver = get_driver()
    try:
        driver.get(url)

        # 国内IPをX-Forwarded-Forに設定（擬似）
        ip = random.choice(DOMESTIC_IPS)
        driver.execute_cdp_cmd(
            'Network.setExtraHTTPHeaders',
            {"headers": {"X-Forwarded-For": ip}}
        )

        time.sleep(5)  # ページ読み込み待機
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        print(f"[{datetime.now()}] クリック成功: {selector}")

    except Exception as e:
        print(f"[{datetime.now()}] エラー発生: {e}")
    finally:
        driver.quit()

# === CSVの読み取りとスケジュール設定 ===
def schedule_tasks():
    with open("tasks.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row["url"]
            selector = row["selector"]
            interval = int(row["interval"])
            unit = row["unit"]

            def make_job(url=url, selector=selector):
                def job():
                    # ゆらぎ －10〜＋10分
                    jitter = random.randint(-10, 10) * 60
                    print(f"[{datetime.now()}] タスク予定: {url} | ゆらぎ: {jitter//60:+}分")
                    time.sleep(abs(jitter))  # ゆらぎ分待機
                    execute_task(url, selector)
                return job

            job = make_job()

            if unit == "時間":
                schedule.every(interval).hours.do(job)
            elif unit == "日":
                schedule.every(interval).days.do(job)
            else:
                print(f"不明な単位: {unit}")

# === メイン ===
if __name__ == "__main__":
    print("📡 自動クリック開始！ Ctrl+C で終了します")
    schedule_tasks()
    while True:
        schedule.run_pending()
        time.sleep(10)