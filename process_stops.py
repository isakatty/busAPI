# import json

# # Read the input JSON file
# with open('converted_station_final.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# # Process each station in the DATA array
# for station in data.get('DATA', []):
#     if 'stop_no' in station:
#         stop_no_str = str(station['stop_no'])
#         if len(stop_no_str) == 4:
#             station['stop_no'] = f"0{stop_no_str}"

# # Write to the output file
# with open('final_stations.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=2)

# print("Processing complete. Output saved to final_stations.json")
