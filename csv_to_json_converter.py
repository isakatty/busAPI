import csv
import json
from typing import List, Dict

def convert_csv_to_json():
    """CSV 파일을 주어진 JSON 형식으로 변환하는 함수"""
    stations = []
    
    # CSV 파일 열기
    with open('chSeoulBusStation.csv', 'r', encoding='utf-8') as csvfile:
        # CSV 헤더 명시적으로 지정
        fieldnames = ['nodeID', 'arsId', 'routeName', 'xcode', 'ycode', 'routeType']
        csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        
        for row in csv_reader:
            station = {
                "nodeID": row.get("nodeID", ""),
                "stop_no": row.get("arsId", ""),
                "routeName": row.get("routeName", ""),
                "ycode": row.get("ycode", ""),
                "xcode": row.get("xcode", ""),
                "routeType": row.get("routeType", ""),
                "nxtStn": ""  # nxtStn 값은 빈 문자열로 설정
            }
            stations.append(station)
    
    # JSON 파일로 저장
    with open('converted_station_final.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(stations, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"Successfully converted {len(stations)} stations")

def main():
    """메인 실행 함수"""
    try:
        convert_csv_to_json()
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == "__main__":
    main()
