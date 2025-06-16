import json

# ars_nxtstn.json 파일 읽기
with open('ars_nxtstn.json', 'r', encoding='utf-8') as f:
    ars_data = json.load(f)
    print(f"Total entries in ars_nxtstn.json: {len(ars_data)}")

# final_stations_copy.json 파일 읽기
with open('final_stations_copy.json', 'r', encoding='utf-8') as f:
    final_data = json.load(f)

# arsId를 기준으로 nxtStn 업데이트
updated_count = 0
for station in final_data['DATA']:
    arsId = station['stop_no']
    
    # ars_nxtstn.json에서 해당 arsId 찾기
    matching_ars = next((item for item in ars_data if item.get('arsId') == arsId), None)
    
    if matching_ars and 'nxtStn' in matching_ars:
        station['nxtStn'] = matching_ars['nxtStn']
        updated_count += 1

print(f"\nUpdated {updated_count} stations with nxtStn values")

# 업데이트된 데이터 저장
with open('final_stations_copy.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("\nProcessing complete. Updated data saved to final_stations_copy.json")
