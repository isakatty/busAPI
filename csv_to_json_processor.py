import csv
import json
from typing import List, Dict

def process_csv_to_json():
    """CSV 파일을 읽어 JSON 형식으로 변환하는 함수"""
    stations = []
    
    # CSV 파일 읽기
    with open('seoulBusStation.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            # 필요한 필드 추출
            try:
                nodeID = int(row['nodeID']) if 'nodeID' in row and row['nodeID'] else None
                arsId = int(row['arsId']) if 'arsId' in row and row['arsId'] else None
                
                routeName = row.get('routeName', '').strip()
                
                # 필수 필드 검증
                if not all([nodeID, arsId, routeName]):
                    continue
                
                station = {
                    'nodeID': nodeID,
                    'arsId': arsId,
                    'routeName': routeName
                }
                stations.append(station)
            except ValueError as e:
                print(f"Error processing row: {str(e)}")
                continue
    
    # 결과를 JSON 파일로 저장
    with open('processed_stations.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(stations, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"Successfully processed {len(stations)} stations")

def main():
    """메인 실행 함수"""
    try:
        process_csv_to_json()
    except Exception as e:
        print(f"Error during processing: {str(e)}")

if __name__ == "__main__":
    main()
