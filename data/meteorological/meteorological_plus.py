import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time

url = 'http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'
service_key = 'ZSG78Pt3T/LihB09c5HOKiwiw7Fp0YO6Zyv3IXdsG6xlAHwXn0Ujh4AI7Qusf257iRAZCZxtR6elbu64sLb2JA=='

station = pd.read_csv('./station_num.csv', header=None)
station_ids = station[0].tolist()

start_year = 1970
end_year = 2024
date_increment = timedelta(days=365)

save_dir = os.path.join("..", "..", "googledrive", "data", "meteorological")
os.makedirs(save_dir, exist_ok=True)

log_file = os.path.join(save_dir, "error_log.txt")
def log_error(message):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

def is_data_saved(station_id, start_dt, end_dt):
    file_name = os.path.join(save_dir, f'station_{station_id}_{start_dt}_{end_dt}.csv')
    return os.path.exists(file_name)

def fetch_data_with_retries(url, params):
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, params=params, timeout=10)
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

for year in range(start_year, end_year + 1):
    print(f"Processing year: {year}")
    year_start_date = datetime(year, 1, 1)
    year_end_date = datetime(year, 12, 31)

    for stn_id in station_ids:
        print(f"Processing station ID: {stn_id}")
        current_date = year_start_date

        while current_date <= year_end_date:
            start_dt = current_date.strftime('%Y%m%d')
            end_dt = min(current_date + date_increment - timedelta(days=1), year_end_date).strftime('%Y%m%d')

            if is_data_saved(stn_id, start_dt, end_dt):
                print(f"Data for station {stn_id} from {start_dt} to {end_dt} already saved. Skipping.")
                current_date += date_increment
                continue

            params = {
                'serviceKey': service_key,
                'pageNo': '1',
                'numOfRows': '999',
                'dataType': 'JSON',
                'dataCd': 'ASOS',
                'dateCd': 'HR',
                'startDt': start_dt,
                'startHh': '00',
                'endDt': end_dt,
                'endHh': '23',
                'stnIds': stn_id
            }

            response = fetch_data_with_retries(url, params)
            if not response:
                log_error(f"Failed to fetch data: station {stn_id}, {start_dt} to {end_dt}")
                current_date += date_increment
                continue

            try:
                data = response.json()
                body = data['response'].get('body', {})
                items = body.get('items', {}).get('item', [])
                if items:
                    df = pd.DataFrame(items)
                    file_name_csv = os.path.join(save_dir, f'station_{stn_id}_{start_dt}_{end_dt}.csv')
                    df.to_csv(file_name_csv, index=False, encoding='utf-8-sig')
                    print(f"Data saved for station {stn_id}, {start_dt} to {end_dt}.")
            except Exception as e:
                log_error(f"Error processing data: station {stn_id}, {start_dt} to {end_dt} - {e}")
            
            current_date += date_increment
