import requests
import time


class RequestRiotAPI:
    def set_api_key(self, api_key):
        self.api_key = api_key

    def request_riot_api(self, request_header):
        time.sleep(0.9)
        while True:
            try:
                result = requests.get(request_header)
                break
            except:
                time.sleep(2)
                continue
        return result.json()

    # CHAMPION-V3
    ## CHAMPION_ROTATION
    def get_champion_rotation(self):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/platform/v3/champion-rotations?api_key={self.api_key}"
        )

    # SUMMONER-V4
    ## SUMMONER_BY_ACCOUNT_ID
    def get_summoner_by_account_id(self, encryptedAccountId):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/summoner/v4/summoners/by-account/{encryptedAccountId}?api_key={self.api_key}"
        )

    ## SUMMONER_BY_SUMMONER_ID
    def get_summoner_by_summoner_id(self, encryptedSummonerId):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/summoner/v4/summoners/{encryptedSummonerId}?api_key={self.api_key}"
        )

    ## SUMMONER_BY_SUMMONER_NAME
    def get_summoner_by_summoner_name(self, summonerName):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={self.api_key}"
        )

    ## SUMMONER_BY_PUU_ID
    def get_summoner_by_puu_id(self, encryptedPUUID):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}?api_key={self.api_key}"
        )

    ## SUMMONER_BY_RSOPUU_ID
    def get_summoner_by_rsopuu_id(self, rsoPUUID):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/fulfillment/v1/summoners/by-puuid/{rsoPUUID}?api_key={self.api_key}"
        )

    ## SUMMONER_ME
    def get_summoner_me(self):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/summoner/v4/summoners/me?api_key={self.api_key}"
        )

    # CHAMPION-MASTERY-V4
    ## 미작성

    # SPECTATOR-V4
    ## 미작성

    # LEAGUE-V4
    ## LEAGUE_BY_QUEUE_TIER_DIVISION (LEAGUE-EXP-V4와 동일하며 챌린저/그랜드 마스터/마스터 티어 정보 반환하지 않음)
    def get_league_by_queue_tier_division(self, queue, tier, division, page=1):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/league/v4/entries/{queue}/{tier}/{division}?page={str(page)}&api_key={self.api_key}"
        )

    # TOURNAMENT-STUB-V4
    ## 미작성

    # AF-2019
    ## 미작성

    # LEAGUE-EXP-V4
    ## LEAGUE_EXP_BY_QUEUE_TIER_DIVISION
    def get_league_exp_by_queue_tier_division(self, queue, tier, division, page=1):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_KR}/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={str(page)}&api_key={self.api_key}"
        )

    # TFT-MATCH-V1
    ## 미작성

    # TFT-SUMMONER-V1
    ## 미작성

    # TFT-LEAGUE-V1
    ## 미작성

    # LOR-RANKED-V1
    ## 미작성

    # CLASH-V1
    ## 미작성

    # VAL-CONTENT-V1
    ## 미작성

    # ACCOUNT-V1
    ## 미작성

    # LOR-MATCH-V1
    ## 미작성

    # VAL-RANKED-V1
    ## 미작성

    # LOL-STATUS-V4
    ## 미작성

    # TFT-STATUS-V1
    ## 미작성

    # LOR-STATUS-V1
    ## 미작성

    # VAL-STATUS-V1
    ## 미작성

    # MATCH-V5
    ## MATCH_BY_PUUID
    def get_match_by_puuid(
        self, puuid, start_time="", end_time="", queue="", type="", start=0, count=20
    ):
        param = ""
        if start_time != "":
            param = param + f"startTime={start_time}&"
        if end_time != "":
            param = param + f"endTime={end_time}&"
        if queue != "":
            param = param + f"queue={queue}&"
        if type != "":
            param = param + f"type={type}&"
        if start != 0:
            param = param + f"start={start}&"
        if count != "":
            param = param + f"count={count}&"
        return self.request_riot_api(
            f"{SERVER_ADDRESS_ASIA}/lol/match/v5/matches/by-puuid/{puuid}/ids?{param}api_key={self.api_key}"
        )

    ## MATCH_BY_MATCHID
    def get_match_by_match_id(self, matchId):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_ASIA}/lol/match/v5/matches/{matchId}?api_key={self.api_key}"
        )

    ## MATCH_TIMELINE_BY_MATCHID
    def get_match_timeline_by_match_id(self, matchId):
        return self.request_riot_api(
            f"{SERVER_ADDRESS_ASIA}/lol/match/v5/matches/{matchId}/timeline?api_key={self.api_key}"
        )

    # LOL-CHALLENGES-V1
    # 미작성


SERVER_ADDRESS_KR = "https://kr.api.riotgames.com"
SERVER_ADDRESS_ASIA = "https://asia.api.riotgames.com"
DEFAULT_QUEUE = "RANKED_SOLO_5x5"

tier_list = [
    "DIAMOND",
    "EMERALD",
    "PLATINUM",
    "GOLD",
    "SILVER",
    "BRONZE",
    "IRON",
]

tier_exp_list = [
    "CHALLENGER",
    "GRANDMASTER",
    "MASTER",
    "DIAMOND",
    "EMERALD",
    "PLATINUM",
    "GOLD",
    "SILVER",
    "BRONZE",
    "IRON",
]

division_list = ["I", "II", "III", "IV"]

target_tier_list = [
    "DIAMOND",
    "EMERALD",
    "PLATINUM",
]

team_position_list = [
    "TOP",
    "JUNGLE",
    "MIDDLE",
    "BOTTOM",
    "UTILITY",
]
