import csv
import time
import random
import schedule
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 国内IPアドレスのサンプル（適宜追加可能）
DOMESTIC_IP_LIST = [
    "133.106.60.123", "103.5.140.1", "110.233.108.99",
    "150.95.255.38", "202.238.152.1"
]

def get_random_headers():
    print("📦 ヘッダーとUAをランダム生成中...")
    browsers = ["Chrome", "Firefox", "Safari"]
    os_choices = ["Windows", "macOS", "iOS", "Android"]
    devices = ["PC", "スマートフォン"]

    device = random.choice(devices)
    os_type = random.choice(["Windows", "macOS"]) if device == "PC" else random.choice(["iOS", "Android"])
    browser = random.choice(browsers)
    user_agent = f"{browser} on {os_type}"

    headers = {
        "User-Agent": user_agent,
        "X-Forwarded-For": random.choice(DOMESTIC_IP_LIST)
    }

    print(f"✅ 使用User-Agent: {headers['User-Agent']}")
    print(f"✅ 使用IP (擬似): {headers['X-Forwarded-For']}")

    return headers

def click_element(url, selector):
    print(f"🔗 {url} にアクセスして {selector} をクリックします")
    headers = get_random_headers()

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # 読み込み待ち
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        print("🖱️ クリック成功")
    except Exception as e:
        print(f"❌ クリック失敗: {e}")
    finally:
        driver.quit()

def schedule_tasks():
    print("📋 タスクCSVを読み込み中...")
    try:
        with open("task.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(f"📄 読み込み行: {row}")
                url = row["url"]
                selector = row["selector"]
                interval = int(row["interval"])
                unit = row["unit"]

                def job(u=url, s=selector):
                    print(f"⏰ {datetime.now()} - {u} 実行中")
                    click_element(u, s)

                jitter = random.randint(-10, 10)  # ゆらぎ（±10分）
                interval_with_jitter = max(1, interval * 60 + jitter)

                if unit == "時間":
                    schedule.every(interval_with_jitter).minutes.do(job)
                elif unit == "日":
                    schedule.every(interval_with_jitter * 60).minutes.do(job)
                else:
                    print(f"⚠️ 未知の単位: {unit}")

                print(f"✅ スケジュール設定済: {url} [{interval} {unit} + ゆらぎ {jitter}分]")

                # 初回即時実行
                job()

    except FileNotFoundError:
        print("❌ task.csv が見つかりません")
    except Exception as e:
        print(f"❌ CSV読み込みエラー: {e}")

print("📡 自動クリック開始！ Ctrl+C で終了します")
schedule_tasks()

while True:
    schedule.run_pending()
    time.sleep(1)