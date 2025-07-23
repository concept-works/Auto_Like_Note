import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
import os
from datetime import datetime

def get_next_ip(ip_file, index_file):
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
        options.add_argument(f"--proxy-server={ip}")

        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1280, 800)  # PCビュー想定

        driver.get(url)

        # 明示的に要素が出現するのを最大10秒待つ
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

        element.click()
        print("✅ クリック成功", flush=True)
        log_click(url, ip, log_file)

    except Exception as e:
        print(f"❌ クリック失敗: {e}", flush=True)
    finally:
        driver.quit()

def schedule_tasks():
    print("📋 タスクスケジュール設定開始", flush=True)

    task_file = os.path.join(os.path.dirname(__file__), 'tasks.csv')
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

        def make_job(u=url, s=selector):
            return lambda: click_element(u, s, get_next_ip(ip_file, index_file), log_file)

        if unit == "分":
            schedule.every(interval).minutes.do(make_job())
        elif unit == "時間":
            schedule.every(interval).hours.do(make_job())
        elif unit == "日":
            schedule.every(interval).days.do(make_job())
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