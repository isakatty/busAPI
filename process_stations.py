import json

# JSON 파일 읽기
with open('final_stations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# nxtStn이 없는 stop_no 찾기
empty_stations = []
for station in data.get('DATA', []):
    if 'nxtStn' not in station or station.get('nxtStn', '') == '':
        empty_stations.append({"no_stop": station.get('stop_no', '')})

# 결과 저장
with open('empty_nxtStn.json', 'w', encoding='utf-8') as f:
    json.dump(empty_stations, f, ensure_ascii=False, indent=2)

print(f"처리 완료: {len(empty_stations)}개의 nxtStn이 없는 정류장 발견")
print(f"정류장 번호들: {[station['no_stop'] for station in empty_stations]}")
