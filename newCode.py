import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os
import time
import os

# 로깅 설정
logging.basicConfig(
    filename='api_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def api_call(arsId):
    """
    API 호출을 수행하고 nxtStn 값을 반환합니다.
    """
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            api_key = config['api_key']
        
        api_url = f'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?arsId={arsId}&ServiceKey={api_key}'
        response = requests.get(api_url)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            msg_header = root.find('./msgHeader')
            header_cd = msg_header.find('./headerCd').text if msg_header is not None else '0'
            
            # headerCd가 7이면 오류로 처리
            if header_cd == '7':
                error_msg = msg_header.find('./headerMsg').text if msg_header is not None else 'Unknown error'
                logging.error(f"Critical error in API response for arsId {arsId}: {error_msg}")
                return None
            
            # headerCd가 4이면 nxtStn을 None으로 설정
            elif header_cd == '4':
                logging.warning(f"API returned headerCd 4 for arsId {arsId}")
                return [None]
            
            msg_body = root.find('./msgBody')
            item_list = msg_body.findall('./itemList')

            if not item_list:
                logging.warning(f"'itemList' not found for arsId {arsId}")
                return []

            # 모든 nxtStn 값을 배열로 저장
            nxtStns = []
            for item in item_list:
                nxt_stn = item.find('./nxtStn')
                if nxt_stn is not None and nxt_stn.text and nxt_stn.text.strip():
                    nxtStns.append(nxt_stn.text.strip())

            if not nxtStns:
                logging.info(f"No nxtStn found for arsId {arsId}")
                return []
            
            return nxtStns

        logging.error(f"API call failed for arsId {arsId}. Status code: {response.status_code}")
        return None

    except ET.ParseError as e:
        logging.error(f"Error parsing XML for arsId {arsId}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error for arsId {arsId}: {e}")
        return None

def main():
    """
    정류소 데이터를 업데이트하고 결과를 저장합니다.
    """
    try:
        # JSON 파일 읽기
        with open('final_stations.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # config.json 읽기
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            api_key = config['api_key'][0]  # 첫 번째 API 키 사용
        
        # 진행 상황 파일이 있는지 확인
        progress_file = 'progress.json'
        start_idx = 1
        
        # 진행 상황 파일이 있으면 마지막 인덱스 불러오기
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                start_idx = progress.get('last_processed', 1)
        
        # API 호출 횟수 추적
        api_calls = 0
        max_api_calls = 1000  # 단일 API 키로 1000회
        total_stops = len(data['DATA'])
        
        print("\nProcessing stations (Press Ctrl+C to stop)...")
        print("-" * 50)
        
        # 각 정류소에 대해 처리
        for idx, stop_data in enumerate(data['DATA'][start_idx-1:], start_idx):
            arsId = stop_data['stop_no']  # stop_no를 그대로 arsId로 사용
            
            # 진행 상황 표시
            print(f"\rProcessing {idx}/{total_stops} ({(idx/total_stops*100):.1f}% complete)", end="")
            
            # API 호출 횟수 체크
            if api_calls >= max_api_calls:
                logging.warning(f"Reached maximum API calls limit ({max_api_calls})")
                print("\nMaximum API calls reached. Stopping process.")
                break
            
            # API 호출 및 nxtStn 업데이트
            nxtStns = api_call(arsId)
            
            # API 응답에서 오류 코드 확인
            if nxtStns is None:
                print(f"\nError: API call returned None for arsId {arsId}")
                logging.error(f"API call returned None for arsId {arsId}")
                print("\nProcess stopped due to API error. Current progress saved.")
                break
            
            # headerCd가 4인 경우 nxtStn을 None으로 설정
            if isinstance(nxtStns, list) and len(nxtStns) == 1 and nxtStns[0] is None:
                nxtStn = None
                print(f"\nAPI returned headerCd 4 for arsId {arsId}")
            else:
                # None이 아닌 첫 번째 값을 찾기
                if isinstance(nxtStns, list):
                    # 배열에서 None이 아닌 첫 번째 값을 찾기
                    nxtStn = next((stn for stn in nxtStns if stn is not None), "")
                    print(f"\nAPI response for arsId {arsId}: {nxtStns}")
                else:
                    nxtStn = nxtStns if nxtStns is not None else ""
            
            stop_data['nxtStn'] = nxtStn
            # stop_no를 string으로 명시적으로 변환하여 저장
            stop_data['stop_no'] = str(stop_data['stop_no'])
            
            # 로깅
            logging.info(f"Updated arsId: {arsId}, nxtStn: {nxtStn}")
            
            # API 호출 횟수 증가
            api_calls += 1
            
            # 진행 상황 저장
            with open(progress_file, 'w') as f:
                json.dump({'last_processed': idx}, f)
            
            # 0.5초 대기 (API 호출 간격 제한)
            time.sleep(0.5)
        
        # 업데이트된 데이터 저장
        with open('final_stations.json', 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=2)
            
        print("\n")
        logging.info(f"Successfully updated {api_calls} stations")
        print(f"Successfully updated {api_calls} stations")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Saving current progress...")
        with open('final_stations.json', 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=2)
        print(f"Successfully saved progress with {api_calls} updated stations")
        logging.info(f"Process interrupted. Saved progress with {api_calls} updated stations")
        
    except Exception as e:
        logging.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main()