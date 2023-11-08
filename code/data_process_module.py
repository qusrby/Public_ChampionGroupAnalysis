import pandas as pd
import numpy as np
import time

import riot_api_request_module as rar  # 라이엇 API 관련
import file_manage_module as fm  # 저장 파일 만들기


# 소환사 리스트 수집
def collect_summoner_list(rrapi: rar.RequestRiotAPI, queue, page_collect):
    for tier in rar.target_tier_list:
        print(f"소환사 리스트 수집 시작 | SUMMONER {str(queue)} {str(tier)}")
        final_result = pd.DataFrame()
        result = pd.DataFrame()

        summoners = fm.get_data_frame(
            f"SUMMONER {str(queue)} {str(tier)}.csv", "data/summoner/"
        )
        page_start = int(1 + (summoners.shape[0] / 205) // 4)

        for division in rar.division_list:
            # 소환사 리스트 불러오기
            for page in range(page_start, page_start + page_collect):
                # 소환사 리스트 수집
                get_df = rrapi.get_league_by_queue_tier_division(
                    queue, tier, division, page
                )
                new_data = pd.DataFrame(get_df)[["tier", "rank", "summonerId"]]

                # 빈 열 생성
                new_data["puuId"] = np.nan
                new_data["status"] = np.nan

                # 엑셀의 #NAME 오류를 방지하기 위해 맨 앞에 공백 삽입
                new_data["summonerId"] = new_data["summonerId"].apply(
                    lambda x: " " + x if not x.startswith(" ") else x
                )
                result = pd.concat([result, new_data])
                print(
                    f"소환사 리스트 수집 중 | SUMMONER {str(queue)} {str(tier)} {str(division)} | PAGE : {page}"
                )
            final_result = pd.concat([summoners, result])
        # 소환사 리스트 저장
        fm.save_file_csv(
            final_result,
            f"SUMMONER {str(queue)} {str(tier)}.csv",
            "data/summoner/",
        )
        print(f"소환사 리스트 수집 완료 | SUMMONER {str(queue)} {str(tier)}")


# 소환사 ID로 PUUID 수집
def summoner_id_to_puu_id(rrapi: rar.RequestRiotAPI, queue):
    for tier in rar.target_tier_list:
        print(f"PUUID 수집 시작 | SUMMONER {str(queue)} {str(tier)}")
        # 소환사 리스트 불러오기
        summoners = fm.get_data_frame(
            f"SUMMONER {str(queue)} {str(tier)}.csv", "data/summoner/"
        )

        # 소환사 ID로 PUUID 수집
        for index, summoner_index in summoners[pd.isna(summoners["puuId"])].iterrows():
            summoner_id = summoner_index["summonerId"]
            new_data = pd.Series(rrapi.get_summoner_by_summoner_id(summoner_id.strip()))

            if not new_data["puuid"].startswith(" "):
                new_data["puuid"] = " " + new_data["puuid"]
            summoners["puuId"] = summoners["puuId"].astype(str)
            summoners.loc[index, "puuId"] = str(new_data["puuid"])

            fm.save_file_csv(
                summoners,
                f"SUMMONER {str(queue)} {str(tier)}.csv",
                "data/summoner/",
            )
            new_data["puuid"] = new_data["puuid"].strip()

            print(
                f"{index} | SUMMONERID : {summoner_id} | {str(queue)} {str(tier)} | PUUID 수집 완료"
            )
        print(f"PUUID 수집 완료 | SUMMONER {str(queue)} {str(tier)}")


# 매치 리스트 수집
def collect_match_list_by_puu_id(
    rrapi: rar.RequestRiotAPI, queue, count, *period:tuple
):
    def record_done(status, text):
        # PUUID 사용 완료 기록
        summoners.loc[index, f"status {p[2]}"] = str(f"{status}")
        fm.save_file_csv(
            summoners,
            f"SUMMONER {str(queue)} {str(tier)}.csv",
            "data/summoner/",
        )
        print(
            f"Index : {index} | PUUID : {summoner_puu_id} | {str(queue)} {str(tier)} | {text} "
        )

    for tier in rar.target_tier_list:
        print(f"매치 수집 시작 | SUMMONER {str(queue)} {str(tier)}")
        # 소환사 리스트 불러오기
        summoners = fm.get_data_frame(
            f"SUMMONER {str(queue)} {str(tier)}.csv", "data/summoner/"
        )
        for p in period:
            if f"status {p[2]}" not in summoners.columns:
                # 컬럼이 없으면 새로운 컬럼을 생성하고 원하는 값을 할당
                summoners[f"status {p[2]}"] = None
        for index, summoner_index in summoners.iterrows():
            for p in period:
                # 매치 리스트 수집
                if summoner_index["puuId"] == None:
                    continue
                if pd.notna(summoner_index[f"status {p[2]}"]):
                    continue
                summoner_puu_id = summoner_index["puuId"].strip()
                get = pd.DataFrame()
                new_data = pd.DataFrame()
                get_part = pd.DataFrame()
                get_part["matchId"] = rrapi.get_match_by_puuid(
                        summoner_puu_id,
                        start_time=p[0],
                        end_time=p[1],
                        type="ranked",
                        start=0,
                        count=count,
                    )

                get_part["version"] = p[2]

                # 데이터 병합
                if get_part.empty == False:  # 지정한 기간에 플레이한 게임이 있는 경우
                    new_data["matchId"] = get_part["matchId"]
                    new_data["puuId"] = summoner_index["puuId"]
                    new_data["tier"] = summoner_index["tier"]
                    new_data["rank"] = summoner_index["rank"]
                    new_data["version"] = get_part["version"]
                    new_data["status"] = np.nan
                    # 매치 리스트 저장
                    if fm.file_exist(f"MATCH {str(queue)} {str(tier)}.csv","data/match/"):
                        fm.append_file_csv(
                            new_data,
                            f"MATCH {str(queue)} {str(tier)}.csv",
                            "data/match/",
                        )
                    else:
                        fm.save_file_csv(
                            new_data,
                            f"MATCH {str(queue)} {str(tier)}.csv",
                            "data/match/",
                        )
                    record_done("Collected", f"{p[2]} 매치 ID 수집 완료")
                else:  # 지정한 기간에 플레이한 게임이 없는 경우
                    record_done("EmptyGameRecord", f"{p[2]} 해당 기간에 플레이한 기록 없음")
                    continue

        print(f"매치 수집 완료 | SUMMONER {str(queue)} {str(tier)}")


# 챔피언 분류 데이터 수집
def collect_champion_list_by_match_id(rrapi: rar.RequestRiotAPI, queue, *period:tuple):
    def record_done(status, text, elapsed):
        # 매치 사용 완료 기록
        matches.loc[index, "status"] = str(f"{status}")
        fm.save_file_csv(
            matches,
            f"MATCH {str(queue)} {str(tier)}.csv",
            "data/match/",
        )
        print(
            f"Index : {index} | MATCH ID : {match_id} | {str(queue)} {str(tier)} | {elapsed:2f}초 | {text}"
        )

    for tier in rar.target_tier_list:
        print(f"챔피언 분류 수집 시작 | MATCH {str(queue)} {str(tier)}")

        # 매치 리스트 불러오기
        matches = fm.get_data_frame(
            f"MATCH {str(queue)} {str(tier)}.csv", "data/match/"
        )

        # 매치 리스트 중복 제거
        matches.drop_duplicates(subset=["matchId"], inplace=True)
        matches.reset_index(inplace=True, drop=True)
        for p in period:
            for index, match_index in matches[matches[f"status"].isna()].iterrows():
                start_time = time.time()
                # 매치 데이터 수집
                match_id = match_index["matchId"]
                match_data = pd.DataFrame(rrapi.get_match_by_match_id(match_id))

                # 데이터를 찾지 못했을 경우
                if "info" not in match_data.columns:
                    end_time = time.time()
                    record_done("Data not found", "데이터 찾지 못함", end_time - start_time)
                    continue

                # 매치 정보 기억
                game_duration = match_data["info"]["gameDuration"]
                game_version = match_data["info"]["gameVersion"]
                game_mode = match_data["info"]["gameMode"]
                game_version = game_version.split(".")
                game_version = ".".join(game_version[0:2])

                # 클래식 랭크 게임이 아닐 경우
                if game_mode != "CLASSIC":
                    end_time = time.time()
                    record_done("Not Classic Mode", "클래식 랭크 게임이 아님", end_time - start_time)
                    continue

                # 20분 미만 매치일 경우
                if game_duration < (60 * 20):
                    end_time = time.time()
                    record_done("Game Duration Too Short", "매치 진행 시간 부족", end_time - start_time)
                    continue

                # 정상 데이터일 경우 세부 정보 꺼내서 합치기
                challenges = pd.DataFrame()
                for part in match_data["info"]["participants"]:
                    df_part = pd.Series(part)
                    challenges = pd.concat([challenges, df_part], axis=1)
                new_data:pd.DataFrame = challenges.transpose()
                new_data = new_data.reset_index(drop=True)
                new_data.drop(["killingSprees", "turretTakedowns"], axis=1, inplace=True) # 기존 데이터에도 있는데, challenges 에도 존재해서 삭제
                new_data["version"] = game_version
                new_data["tier"] = tier
                new_data = pd.concat(
                    [
                        new_data.drop(["challenges"], axis=1),
                        pd.json_normalize(new_data["challenges"]),
                    ],
                    axis=1,
                )

                new_data.fillna(0, inplace=True)
                fm.save_file_csv(
                    new_data,
                    f"CHAMPION {str(queue)} {game_version} {str(tier)} {match_id}.csv",
                    "data/champion/",
                )

                end_time = time.time()
                record_done("Collected", "챔피언 분류 데이터 수집 완료", end_time - start_time)

        print(f"챔피언 분류 수집 종료 | MATCH {str(queue)} {str(tier)}")
