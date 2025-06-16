import json
import requests
import xml.etree.ElementTree as ET
import xmltodict
import time
from typing import List, Dict, Optional

class BusStation:
    def __init__(self, nodeID: int, arsId: int, routeName: str):
        self.nodeID = nodeID
        self.arsId = arsId
        self.routeName = routeName

def get_api_key() -> str:
    """API 키를 config.json에서 읽어오는 함수"""
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        return config['api_key']

def get_next_station(arsId: int) -> Optional[str]:
    """주어진 arsId에 대한 다음 정류장 정보를 조회하는 함수"""
    api_key = get_api_key()
    api_url = f'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey={api_key}&arsId={arsId}'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            msg_header = root.find('./msgHeader')
            
            if msg_header is not None and msg_header.find('./headerCd').text != '0':
                return None
            
            msg_body = root.find('./msgBody')
            item_list = msg_body.findall('./itemList')

            if not item_list:
                return None

            for item in item_list:
                nxt_stn = item.find('./nxtStn').text.strip()
                if nxt_stn:
                    return nxt_stn

            return None

        except ET.ParseError:
            return None
    
    return None

def process_stations() -> List[Dict]:
    """정류장 데이터를 처리하여 새로운 데이터 모델로 변환하는 함수"""
    stations = []
    
    # JSON 파일에서 데이터 읽기
    with open('new_stationList.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 각 정류장 처리
    for stop_data in data['DATA']:
        arsId = stop_data['stop_no']
        next_station = get_next_station(arsId)
        
        if next_station:
            station = {
                'nodeID': stop_data.get('nodeID', arsId),  # nodeID가 없으면 arsId로 대체
                'arsId': arsId,
                'routeName': next_station
            }
            stations.append(station)
    
    return stations

def main():
    """메인 실행 함수"""
    try:
        processed_stations = process_stations()
        
        # 결과를 JSON 파일로 저장
        with open('processed_stations.json', 'w', encoding='utf-8') as output_file:
            json.dump(processed_stations, output_file, ensure_ascii=False, indent=2)
            
        print(f"Successfully processed {len(processed_stations)} stations")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")

if __name__ == "__main__":
    main()
