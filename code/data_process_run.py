import time
import datetime

import riot_api_request_module as rar  # 라이엇 API 관련
import data_process_module as dc

# 기본 설정
with open('api_key.txt', 'r') as file:
    ak = file.read().strip()  # 파일에서 읽은 내용에서 앞뒤 공백 제거
queue = rar.DEFAULT_QUEUE  # 게임의 기본 큐 타입

# 라이엇 API 세팅
rrapi = rar.RequestRiotAPI()
rrapi.set_api_key(ak)

# 소환사 리스트 수집
dc.collect_summoner_list(rrapi, queue, 3)

# 소환사 ID로 PUUID 수집
dc.summoner_id_to_puu_id(rrapi, queue)

# 매치 리스트 수집
# 8월 16일부터 8월 29일까지는 13.16
start_date_time = datetime.datetime(2023, 8, 17, 0, 0, 0)
end_date_time = datetime.datetime(2023, 8, 28, 0, 0, 0)
start_date_time_epoch = str(int(time.mktime(start_date_time.timetuple())))
end_date_time_epoch = str(int(time.mktime(end_date_time.timetuple())))
v1 = [start_date_time_epoch, end_date_time_epoch, "13.16"]

# 8월 30일부터 9월 13일까지는 13.17
start_date_time = datetime.datetime(2023, 8, 30, 0, 0, 0)
end_date_time = datetime.datetime(2023, 9, 13, 0, 0, 0)
start_date_time_epoch = str(int(time.mktime(start_date_time.timetuple())))
end_date_time_epoch = str(int(time.mktime(end_date_time.timetuple())))
v2 = [start_date_time_epoch, end_date_time_epoch, "13.17"]

# 9월 14일부터 9월 27일까지는 13.18
start_date_time = datetime.datetime(2023, 9, 14, 0, 0, 0)
end_date_time = datetime.datetime(2023, 9, 27, 0, 0, 0)
start_date_time_epoch = str(int(time.mktime(start_date_time.timetuple())))
end_date_time_epoch = str(int(time.mktime(end_date_time.timetuple())))
v3 = [start_date_time_epoch, end_date_time_epoch, "13.18"]

# 매치 리스트 수집
dc.collect_match_list_by_puu_id(rrapi, queue, 10, v3)

# 챔피언 분류 데이터 수집
dc.collect_champion_list_by_match_id(rrapi, queue, v3)
