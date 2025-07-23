import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import schedule
import os
from datetime import datetime

def log_click(url):
    log_path = os.path.join(os.path.dirname(__file__), 'click_log.csv')
    now = datetime.now().isoformat()
    ip = "60.69.77.243"  # IPローテーションがまだないので仮
    try:
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write("url,click,ip\n")
        with open(log_path, 'a') as f:
            f.write(f"{url},{now},{ip}\n")
        print(f"📝 クリックログ記録: {url}, {now}, {ip}", flush=True)
    except Exception as e:
        print(f"⚠️ クリックログ保存エラー: {e}", flush=True)

def click_element(url, selector):
    print(f"▶️ click_element実行: {url} / {selector}", flush=True)
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        element = driver.find_element("css selector", selector)
        element.click()
        print("✅ クリック成功", flush=True)
        driver.quit()

        log_click(url)

    except Exception as e:
        print(f"❌ クリック失敗: {e}", flush=True)

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