from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import time

# ✅ headless 옵션 (GitHub Actions 서버 환경 필수)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.mobilelegends.com/rank")
time.sleep(7)

# ALL 드롭다운 클릭
dropdowns = driver.find_elements(By.XPATH, "//div[contains(@class,'mt-dropdown')]")
all_dropdown = dropdowns[4]
driver.execute_script("arguments[0].click();", all_dropdown)
time.sleep(2)

# Mythical Glory+ 선택
dropdown_list = dropdowns[5]
option = dropdown_list.find_element(By.XPATH, ".//span[text()='Mythical Glory+']")
driver.execute_script("arguments[0].click();", option)
time.sleep(5)

# 스크롤로 전체 데이터 로드
last_count = 0
while True:
    rows = driver.find_elements(By.CSS_SELECTOR, ".mt-list-layout .mt-list-item")
    current_count = len(rows)
    driver.execute_script("arguments[0].scrollIntoView();", rows[-1])
    time.sleep(2)
    if current_count == last_count:
        break
    last_count = current_count

# 데이터 수집
rows = driver.find_elements(By.CSS_SELECTOR, ".mt-list-layout .mt-list-item")
data = []
for row in rows:
    try:
        hero = row.find_element(By.CSS_SELECTOR, ".mt-2693412 span").text
        pick_rate = row.find_element(By.CSS_SELECTOR, ".mt-2684925 span").text
        win_rate = row.find_element(By.CSS_SELECTOR, ".mt-2684926 span").text
        ban_rate = row.find_element(By.CSS_SELECTOR, ".mt-2687632 span").text
        data.append({"hero": hero, "pick_rate": pick_rate, "win_rate": win_rate, "ban_rate": ban_rate})
    except:
        continue

driver.quit()

# win_ban_sum 컬럼 추가 및 정렬
df = pd.DataFrame(data)
df["win_rate_f"] = df["win_rate"].str.replace("%", "").astype(float)
df["ban_rate_f"] = df["ban_rate"].str.replace("%", "").astype(float)
df["win_ban_sum_f"] = df["win_rate_f"] + df["ban_rate_f"]
df["win_ban_sum"] = df["win_ban_sum_f"].map(lambda x: f"{x:.2f}%")
df = df.drop(columns=["win_rate_f", "ban_rate_f", "win_ban_sum_f"])
df = df.sort_values("win_ban_sum", ascending=False).reset_index(drop=True)

# index.html 저장
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MLBB Mythical Glory+ Stats</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>MLBB Mythical Glory+ Hero Stats</h2>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    {df.to_html(index=False)}
</body>
</html>
"""
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("완료!")