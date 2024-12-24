import requests
import pandas as pd
from datetime import datetime, timedelta

url = 'http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'
service_key = 'ZSG78Pt3T/LihB09c5HOKiwiw7Fp0YO6Zyv3IXdsG6xlAHwXn0Ujh4AI7Qusf257iRAZCZxtR6elbu64sLb2JA=='

station = pd.read_csv('./station_num.csv', header=None)
station_ids = station[0].tolist()

start_year = 1970
end_year = 2024
date_increment = timedelta(days=30)

# 연도별 데이터 수집 및 저장
for year in range(start_year, end_year + 1):
    print(f"Processing year: {year}")
    year_start_date = datetime(year, 1, 1)
    year_end_date = datetime(year, 12, 31) if year != end_year else datetime(end_year, 12, 1)

    for stn_id in station_ids:
        print(f"Processing station ID: {stn_id}")
        current_date = year_start_date
        year_data = []

        while current_date <= year_end_date:
            start_dt = current_date.strftime('%Y%m%d')
            end_dt = min(current_date + date_increment - timedelta(days=1), year_end_date).strftime('%Y%m%d')

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

            while True:
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    if response.headers.get('Content-Type') == 'application/json':
                        try:
                            data = response.json()

                            if 'response' in data and 'header' in data['response']:
                                result_code = data['response']['header'].get('resultCode', '')
                                result_msg = data['response']['header'].get('resultMsg', '')

                                if result_code == '00':  
                                    body = data['response'].get('body', {})
                                    items = body.get('items', {}).get('item', [])
                                    year_data.extend(items)

                                    total_count = int(body.get('totalCount', 0))
                                    current_page = int(params['pageNo'])
                                    if current_page * int(params['numOfRows']) >= total_count:
                                        break
                                    else:
                                        params['pageNo'] = str(current_page + 1)
                                elif result_code == '03': 
                                    print(f"No data for station {stn_id} from {start_dt} to {end_dt}.")
                                    break
                                else:  
                                    print(f"API Error: {result_code}, Message: {result_msg}")
                                    break
                            else:
                                print("Invalid API response format.")
                                break
                        except ValueError:
                            print("Response is not valid JSON. Content:", response.text)
                            break
                    else:
                        
                        break
                else:
                    print(f"HTTP Error {response.status_code}: {response.text}")
                    break

            # 날짜 범위 증가
            current_date += date_increment

        # 해당 관측소의 연도별 데이터 저장
        if year_data:
            df = pd.DataFrame(year_data)
            df = df[['tm', 'stnId', 'stnNm', 'ta']]
            file_name_csv = f'all_station_ta_data_{year}_{stn_id}.csv'
            file_name_json = f'all_station_ta_data_{year}_{stn_id}.json'
            df.to_csv(file_name_csv, index=False, encoding='utf-8-sig')
            df.to_json(file_name_json, orient='records', lines=True, force_ascii=False)
            print(f"Data for station {stn_id} in year {year} saved to {file_name_csv} and {file_name_json}.")
        else:
            print(f"No data collected for station {stn_id} in year {year}.")