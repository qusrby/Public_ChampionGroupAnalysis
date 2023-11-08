import riot_api_request_module as rar  # 라이엇 API 관련
import data_analysis_module as da

# 기본 설정
with open('api_key.txt', 'r', encoding='utf-8') as file:
    ak = file.read().strip()  # 파일에서 읽은 내용에서 앞뒤 공백 제거
queue = rar.DEFAULT_QUEUE  # 게임의 기본 큐 타입

# 라이엇 API 세팅
rrapi = rar.RequestRiotAPI()
rrapi.set_api_key(ak)

# 분석 진행
ver1 = "13.16"
ver2 = "13.17"
ver3 = "13.18"
da.process_champion_data(queue, ver1, ver2, ver3)
da.compare_champion_data(queue, ver1, ver2, ver3)
