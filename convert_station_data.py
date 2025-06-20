import asyncio
import aiohttp
import json
import xml.etree.ElementTree as ET
from aiohttp import ClientSession, ClientTimeout
import logging
import os

logging.basicConfig(level=logging.INFO)

API_KEY_USAGE_LIMIT = 1000  # 한 API 키당 최대 호출 횟수
CONCURRENT_REQUESTS = 10    # 동시에 요청할 수 있는 수 제한

with open('config.json', 'r') as f:
    CONFIG = json.load(f)
    API_KEYS = CONFIG['api_keys']

current_key_index = 0
key_usage_count = 0
API_SEMAPHORE = asyncio.Semaphore(CONCURRENT_REQUESTS)
FAILED_ARS_IDS = []

def get_next_api_key():
    global current_key_index, key_usage_count
    if key_usage_count >= API_KEY_USAGE_LIMIT:
        current_key_index += 1
        key_usage_count = 0
        if current_key_index >= len(API_KEYS):
            raise Exception("모든 API 키 사용량 초과")
    key_usage_count += 1
    return API_KEYS[current_key_index]

async def fetch_nxtStn(session: ClientSession, arsId: str):
    async with API_SEMAPHORE:
        try:
            api_key = get_next_api_key()
            url = f"http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?arsId={arsId}&ServiceKey={api_key}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    logging.warning(f"Status {resp.status} for arsId {arsId}")
                    FAILED_ARS_IDS.append(arsId)
                    return arsId, None
                text = await resp.text()
                root = ET.fromstring(text)

                headerCd = root.findtext('./msgHeader/headerCd', default='0')
                if headerCd == '7':
                    FAILED_ARS_IDS.append(arsId)
                    return arsId, None
                elif headerCd == '4':
                    return arsId, "막차"

                nxtStns = [
                    item.findtext('./nxtStn').strip()
                    for item in root.findall('./msgBody/itemList')
                    if item.find('./nxtStn') is not None and item.findtext('./nxtStn').strip()
                ]
                
                if not nxtStns:
                    nxtStn = None
                else:
                    from collections import Counter
                    most_common = Counter(nxtStns).most_common()
                    nxtStn = most_common[0][0] if most_common else nxtStns[0]
                return arsId, nxtStn

        except Exception as e:
            logging.error(f"Error for arsId {arsId}: {e}")
            FAILED_ARS_IDS.append(arsId)
            return arsId, None

async def main():
    with open('final_stations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    ars_ids = [str(stop['stop_no']) for stop in data['DATA']]
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    timeout = ClientTimeout(total=10)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_nxtStn(session, arsId) for arsId in ars_ids]
        results = await asyncio.gather(*tasks)

    ars_to_nxtStn = dict(results)
    for stop in data['DATA']:
        stop['nxtStn'] = ars_to_nxtStn.get(str(stop['stop_no']))
        stop['stop_no'] = str(stop['stop_no'])

    with open('final_stations.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open('failed_ars_ids.json', 'w', encoding='utf-8') as f:
        json.dump(FAILED_ARS_IDS, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Completed. Updated {len(results)} stops.")
    print(f"❌ Failed arsIds saved to failed_ars_ids.json ({len(FAILED_ARS_IDS)} entries)")

if __name__ == '__main__':
    asyncio.run(main())
