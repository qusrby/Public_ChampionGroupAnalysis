import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

import riot_api_request_module as rar  # 라이엇 API 관련
import file_manage_module as fm  # 저장 파일 만들기

mpl.rcParams["font.family"] = "Noto Sans KR"
mpl.rcParams["axes.unicode_minus"] = False

warnings.filterwarnings("ignore")

def process_champion_data(queue, *versions: str):
    print("챔피언 유사성 분석 시작")

    folder_path = "data/champion/"
    data_list = []  # 빈 리스트 생성

    for idx, filename in enumerate(os.listdir(folder_path)):
        k = 0
        new = fm.read_file_csv(filename, folder_path, hdr=k, encoding="CP949")
        data_list.append(new)  # 데이터를 리스트에 추가
        if (idx > 0) and (idx % 1000) == 0:
            print(f"{idx}개 데이터 로드 완료")

    # 리스트의 데이터를 합쳐서 DataFrame으로 만듦
    df_origin = pd.concat(data_list, axis=0, ignore_index=True)

    # 챔피언 유사성 분석
    for team_position in rar.team_position_list:
        df_v = pd.DataFrame()
        df_filter = df_origin
        for target_version in versions:
            df = df_filter[
                df_filter["version"] == float(target_version)
            ]  # 지정한 버전의 매치만 사용
            df = df[df["hadAfkTeammate"] == 0]  # 자리를 비운 팀원이 존재하는 매치 제외

            # 픽률 필터링
            df = df[df["teamPosition"] == team_position]
            team_position_data_size = df.shape[0]
            min_pick_count = team_position_data_size * 0.01
            df = df[
                df.groupby("championName")["championName"].transform("count")
                > min_pick_count
            ]

            # 데이터 가공

            # > 기반 능력치
            df["magicDamageDealtToChampions rate"] = (
                df["magicDamageDealtToChampions"] / df["totalDamageDealtToChampions"]
            )

            # > 군중 제어 능력
            df["totalTimeCCDealt per minute"] = (
                df["totalTimeCCDealt"] / df["gameLength"] * 60
            )

            # > 강력 군중 제어 능력
            df["enemyChampionImmobilizations per minute"] = (
                df["enemyChampionImmobilizations"] / df["gameLength"] * 60
            )

            # > 암살 능력
            df["soloKills per minute"] = (
                df["soloKills"] / df["gameLength"] * 60
            )

            # > 치유 특성
            df["totalHeal per minute"] = df["totalHeal"] / df["gameLength"] * 60

            # > 치유 및 보호막 특성
            df["effectiveHealAndShielding per minute"] = (
                df["effectiveHealAndShielding"] / df["gameLength"] * 60
            )

            # > 한타 중 생존력
            df["survivedThreeImmobilizesInFight per minute"] = (
                df["survivedThreeImmobilizesInFight"] / df["gameLength"] * 60
            )

            # > 라인 클리어 능력
            df["twentyMinionsIn3SecondsCount per minute"] = (
                df["twentyMinionsIn3SecondsCount"] / df["gameLength"] * 60
            )

            # 필요한 열만 남기기
            df = df[
                [
                    "championName",
                    "teamPosition",
                    "magicDamageDealtToChampions rate",  # 기반 능력치
                    "teamDamagePercentage",  # 딜링 능력
                    "damageTakenOnTeamPercentage",  # 탱킹 능력
                    "totalTimeCCDealt per minute",  # 군중 제어 능력
                    "enemyChampionImmobilizations per minute",  # 강력 군중 제어 능력
                    "killParticipation",  # 한타 기여도
                    "soloKills per minute",  # 암살 능력
                    "totalHeal per minute",  # 힐링 능력
                    "effectiveHealAndShielding per minute",  # 치유 및 보호막 능력
                    "survivedThreeImmobilizesInFight per minute",  # 한타 중 생존력
                    "twentyMinionsIn3SecondsCount per minute",  # 라인 클리어 능력
                    "soloTurretsLategame",  # 스플릿 능력
                    "turretPlatesTaken",  # 초반 포탑 철거 능력
                ]
            ]

            # 분석할 열을 제외한 열만 선택
            selected_columns = df.drop(columns=["championName", "teamPosition"])

            # 정규화를 위한 스케일러 생성 및 적용
            scaler = StandardScaler()
            normalized_columns = scaler.fit_transform(selected_columns)

            # 정규화된 열을 데이터프레임으로 변환
            normalized_df = pd.DataFrame(
                normalized_columns, columns=selected_columns.columns
            )

            # 원본 데이터프레임과 챔피언 이름 합치기
            normalized_df = pd.concat(
                [
                    df["championName"].reset_index(drop=True),
                    normalized_df.reset_index(drop=True),
                ],
                axis=1,
            )
            normalized_df = normalized_df.fillna(0)
            normalized_df = normalized_df.groupby("championName").mean().reset_index()
            normalized_df["version"] = target_version
            df_v = pd.concat([df_v, normalized_df])
            print(f"{team_position} {target_version} 완료")

        df_v.reset_index(inplace=True, drop=True)
        
        # 차원 축소 전 결과 저장
        fm.save_file_csv(
            df_v,
            f"RESULT {str(queue)} {team_position}.csv",
            "result/normalized/",
        )

        # 차원 축소
        model = TSNE(n_components=2, perplexity=30, random_state=42)
        champions_2d = model.fit_transform(
            df_v.drop(columns=["championName", "version"])
        )
        champions_2d = pd.DataFrame(champions_2d, columns=["X", "Y"])

        # 결과 저장
        result = pd.concat(
            [df_v["championName"], champions_2d, df_v["version"]], axis=1
        )
        fm.save_file_csv(
            result,
            f"2D RESULT {str(queue)} {team_position}.csv",
            "result/2d/",
        )

    print("챔피언 유사성 분석 종료")


def compare_champion_data(queue, *versions: str):
    print("시각화 시작")

    colors = ["#91bee5", "#1c619b", "#142b3d"]

    champion_name = fm.get_data_frame("League of Legends Champion List.csv")
    for team_position in rar.team_position_list:
        data = fm.get_data_frame(
            f"2D RESULT {str(queue)} {team_position}.csv", "result/2d/"
        )
        data = data.merge(champion_name, on="championName", how="left")
        data["line"] = 0

        # 데이터의 평균 계산
        mean_x = np.mean(data["X"])
        mean_y = np.mean(data["Y"])

        # 데이터에서 평균 값을 뺴서 원점으로 이동
        data["X"] = data["X"] - mean_x
        data["Y"] = data["Y"] - mean_y

        # 시각화
        plt.figure(figsize=(16, 16))  # 창 크기 조절
        plt.subplots_adjust(0.05, 0.1, 0.95, 0.9)
        plt.axis('equal')
        plt.grid(True, linewidth=0.5, color='gray', linestyle='--')

        var_min = min(round(data["X"].min()),round(data["Y"].min()))
        var_max = max(round(data["X"].max()),round(data["Y"].max()))
        plt.xticks(np.arange(var_min-2, var_max+2, 2))
        plt.yticks(np.arange(var_min-2, var_max+2, 2))

        data["versionCount"] = data.groupby("championName")["version"].transform(
            "count"
        )

        # 그래프 그리기
        for i, version in enumerate(versions):
            # data에서 version과 일치하는 행만 선택합니다.
            subset = data[data["version"] == float(version)]
            # subset의 X와 Y를 산점도로 그립니다.
            plt.scatter(
                subset["X"], subset["Y"], s=12, zorder=5, c=colors[i], label=version
            )

        # 챔피언별로 데이터를 그룹화합니다.
        grouped = data.groupby("championName")

        # 챔피언별로 선을 그립니다.
        for champion, group in grouped:
            group = group.sort_values(by="version")  # 버전순으로 정렬
            x_values = group["X"]
            y_values = group["Y"]
            plt.plot(
                x_values,
                y_values,
                linestyle="--",
                color="gray",
                linewidth=1,
                zorder=3,
            )

        # 챔피언 이름을 데이터 포인트 위에 표시
        latest_versions = data.groupby("championNameKOR")["version"].idxmax()
        latest_data = data.loc[latest_versions]

        # 챔피언 이름을 X, Y 좌표 위에 표시합니다.
        for index, row in latest_data.iterrows():
            plt.annotate(
                row["championNameKOR"],
                (row["X"], row["Y"]),
                textcoords="offset points",
                xytext=(0, -18),
                ha="center",
                fontsize=10,
                zorder=10,
            )

        if team_position == "TOP":
            lane = "탑 라이너"
        elif team_position == "JUNGLE":
            lane = "정글러"
        elif team_position == "MIDDLE":
            lane = "미드 라이너"
        elif team_position == "BOTTOM":
            lane = "원거리 딜러"
        elif team_position == "UTILITY":
            lane = "서포터"

        plt.title(f"챔피언 유사성 시각화 [{lane}]", fontsize=20, y=1.04)
        plt.legend(loc="upper right")
        plt.savefig(f"챔피언 유사성 시각화 [{lane}].png", dpi=300)

    print("시각화 종료")
