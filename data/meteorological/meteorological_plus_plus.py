import os
import json
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# 설정
save_dir = os.path.join("..", "..", "googledrive", "data", "meteorological")
os.makedirs(save_dir, exist_ok=True)

log_file = os.path.join(save_dir, "error_log.txt")

def log_error(message):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

def is_data_saved_json(station_id, start_dt, end_dt):
    file_name = os.path.join(save_dir, f'station_{station_id}_{start_dt}_{end_dt}.json')
    return os.path.exists(file_name)

def fetch_data_with_retries(api, params):
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(api["url"], params=params, timeout=5)
            if response.status_code == 200:
                return response
            else:
                print(f"HTTP Error {response.status_code}: Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
        retries += 1
        time.sleep(RETRY_DELAY)
    print(f"Failed to fetch data after {MAX_RETRIES} retries.")
    return None

# API 정보
apis = [
    {
        "url": "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList",
        "key": "ZSG78Pt3T/LihB09c5HOKiwiw7Fp0YO6Zyv3IXdsG6xlAHwXn0Ujh4AI7Qusf257iRAZCZxtR6elbu64sLb2JA==",
        "limit": 10000
    },
    {
        "url": "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList",
        "key": "sj40PraKG7dGcBNarkyuQo1EcwXDwDORJi1Hz103NVmLD4NBFkyIHBiEnGw/XnL8pKczzFOJh5+qlCtxwRCBDw==",
        "limit": 10000
    },
    {
        "url": "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php",
        "key": "QxivqrPbSjeYr6qz2-o3Fg",
        "limit": 20000
    }
]

# 스테이션 데이터 불러오기
station = pd.read_csv('./station_num.csv', header=None)
station_ids = station[0].tolist()

# API 호출 및 키 관리
api_index = 0
api_calls = 0

for year in range(2003, 2024 + 1):
    print(f"Processing year: {year}")
    year_start_date = datetime(year, 1, 1)
    year_end_date = datetime(year, 12, 31)

    for station_id in station_ids:
        print(f"Processing station ID: {station_id}")
        current_date = year_start_date

        while current_date <= year_end_date:
            # API 호출 한도 초과 시 전환
            if api_calls >= apis[api_index]["limit"]:
                print(f"API limit reached for key {api_index + 1}. Switching to next key...")
                api_index = (api_index + 1) % len(apis)
                api_calls = 0
                if api_index == 0:
                    print("All keys exhausted. Waiting for reset...")
                    time.sleep(86400)  # 1일 대기

            start_dt = current_date.strftime('%Y%m%d')
            end_dt = (current_date + timedelta(days=41) - timedelta(days=1)).strftime('%Y%m%d')

            if is_data_saved_json(station_id, start_dt, end_dt):
                print(f"Data already saved for station {station_id}, {start_dt} to {end_dt}. Skipping...")
                current_date += timedelta(days=41)
                continue

            params = {
                'serviceKey': apis[api_index]["key"],
                'pageNo': '1',
                'numOfRows': '999',
                'dataType': 'JSON',
                'dataCd': 'ASOS',
                'dateCd': 'HR',
                'startDt': start_dt,
                'startHh': '00',
                'endDt': end_dt,
                'endHh': '23',
            }
            if "kma_sfctm2.php" in apis[api_index]["url"]:
                params["stnIds"] = station_id

            response = fetch_data_with_retries(apis[api_index], params)
            api_calls += 1

            if response:
                try:
                    # JSON 저장
                    json_data = response.json()
                    save_path = os.path.join(save_dir, f'station_{station_id}_{start_dt}_{end_dt}.json')
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)
                    print(f"Data saved for station {station_id}, {start_dt} to {end_dt}.")
                except Exception as e:
                    log_error(f"Error saving data for station {station_id}, {start_dt} to {end_dt}: {e}")
            else:
                log_error(f"No response received for station {station_id}, {start_dt} to {end_dt}")

            current_date += timedelta(days=41)
