import csv
import random
import time
import schedule
import pandas as pd
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 国内IPアドレスの例（必要に応じて増やしてください）
JP_IP_LIST = [
    "133.130.90.1", "153.127.200.3", "157.7.150.10", "160.16.220.20"
]

# ランダムなUser-Agentを生成
def generate_user_agent():
    browsers = ["Chrome", "Firefox", "Safari"]
    os_list = {
        "PC": ["Windows NT 10.0", "Macintosh; Intel Mac OS X 10_15_7"],
        "SP": ["iPhone; CPU iPhone OS 14_0 like Mac OS X", "Linux; Android 10"]
    }
    device = random.choice(["PC", "SP"])
    browser = random.choice(browsers)
    os = random.choice(os_list[device])

    if browser == "Chrome":
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    elif browser == "Firefox":
        return f"Mozilla/5.0 ({os}; rv:108.0) Gecko/20100101 Firefox/108.0"
    elif browser == "Safari":
        return f"Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
    return "Mozilla/5.0"

# セレクタをクリックする処理
def click_element(url, selector):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        user_agent = generate_user_agent()
        fake_ip = random.choice(JP_IP_LIST)

        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument(f'--header=X-Forwarded-For:{fake_ip}')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # ページの読み込み待ち

        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        print(f"[{datetime.now()}] ✅ Clicked: {url}")
        driver.quit()
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {url} - {str(e)}")

# 各行ごとにスケジュールを設定
def schedule_tasks():
    try:
        with open("task.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"📋 ヘッダー確認: {reader.fieldnames}")
            for row in reader:
                try:
                    url = row["url"]
                    selector = row["selector"]
                    interval = int(row["interval"])
                    unit = row["unit"]

                    def job(u=url, s=selector):
                        print(f"[{datetime.now()}] 🔁 Running task: {u}")
                        click_element(u, s)

                    # ゆらぎ（-10〜+10分）を追加
                    jitter_minutes = random.randint(-10, 10)
                    actual_interval = interval * 60 + jitter_minutes

                    if unit == "時間":
                        schedule.every(actual_interval).minutes.do(job)
                    elif unit == "日":
                        schedule.every(interval).days.do(job)
                    else:
                        print(f"⚠️ 不正なunit: {unit}（{url}）")

                except KeyError as e:
                    print(f"⚠️ KeyError: {e} in row: {row}")
                except Exception as e:
                    print(f"⚠️ 予期せぬエラー: {e}")

    except FileNotFoundError:
        print("🚫 task.csv が見つかりません")
    except Exception as e:
        print(f"🚫 CSV読み込み時のエラー: {e}")

# メインループ
def main_loop():
    print("📡 自動クリック開始！ Ctrl+C で終了します")
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    schedule_tasks()
    main_loop()