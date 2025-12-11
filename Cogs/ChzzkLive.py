# 디스코드 모듈
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View  # 버튼 사용을 위해

# API 호출 모듈
import requests, json

# 날짜 계산 모듈
from datetime import datetime

import random
import string

# 환경 변수 파일 불러오기를 위해 import.
import os
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()


# 시간 변환기 (현재 시간 - 방송 진행 시간)
def convert_time(totalTime):
    # 총 초를 구함
    totalSeconds = totalTime.total_seconds()

    # 시간, 분, 초 계산
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 출력 포맷 설정
    formattedTime = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    return formattedTime


# API 호출을 위한 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


# ===== 치지직 채널 검색 API =====
class Chzzk(commands.Cog, name="치지직"):
    def __init__(self, bot):
        self.bot = bot

    # 치지직 스트리머 채널 라이브 상태 확인 command
    @app_commands.command(
        name="치지직",
        description="입력한 채널명으로 스트리머의 채널 정보를 알려드릴게요!",
    )
    @app_commands.describe(채널_이름="검색하고 싶은 치지직 채널 이름")
    async def chzzk_info(self, interaction: discord.Interaction, 채널_이름: str):
        # {channel(채널명)}로 치지직 스트리머 채널 검색
        base_url = os.getenv("CHZZK_API_URL")
        params = {
            "keyword": 채널_이름,
            "offset": 0,
            "size": 1,
            "withFirstChannelContent": True,
        }

        channel_response = json.loads(
            requests.get(base_url, headers=headers, params=params).text
        )

        # channelUrl = f"https://api.chzzk.naver.com/service/v1/search/channels?keyword='{채널_이름}'&offset=0&size=1&withFirstChannelContent=True"
        # channelResponse = json.loads(requests.get(channelUrl, headers=headers).text)

        # 검색 완료된 스트리머 채널 정보
        channel_info = channel_response["content"]["data"][0]["channel"]
        # 검색 완료된 스트리머 라이브 정보
        live_info = channel_response["content"]["data"][0]["content"]["live"]

        # 채널 url 이동을 위한 버튼
        button = Button(
            label=f"{channel_info['channelName']} 채널 바로가기",
            url=f"https://chzzk.naver.com/live/{channel_info['channelId']}",
        )
        view = View()
        view.add_item(button)

        # 출력 =====================================================================================================
        # 1) 현재 라이브 정보가 있으면,
        if live_info != None:
            # 현재 시간 구하기
            current_time = datetime.now()
            # 방송 진행 시간 구하기
            streanTime = convert_time(
                current_time
                - datetime.strptime(live_info["openDate"], "%Y-%m-%d %H:%M:%S")
            )

            # discord에 추가할 embed 생성
            embed = discord.Embed(
                title="치지직에서 생방송 중인 스트리머의 정보에요!", color=0xFFFFFF
            )

            # 이미지가 변경이 안되면, 아래 77~92줄(현재 방송썸네일 이미지 / url에 랜덤 파라미터 추가) 참고
            # embed에 썸네일 사진 (스트리머 사진) 추가
            embed.set_thumbnail(url=channel_info["channelImageUrl"])

            # enbed에 field 추가
            embed.add_field(
                name="스트리머 명", value=channel_info["channelName"], inline=False
            )
            embed.add_field(
                name="방송 제목", value=live_info["liveTitle"], inline=False
            )
            embed.add_field(
                name="시청자 수",
                value=f"{format(live_info['concurrentUserCount'], ',')} 명",
                inline=False,
            )
            embed.add_field(name="방송 시간", value=streanTime, inline=False)
            if live_info["liveCategoryValue"] != "":
                embed.add_field(
                    name="카테고리", value=live_info["liveCategoryValue"], inline=False
                )
            else:
                embed.add_field(name="카테고리", value="없음", inline=False)

            # ===== embed에 방송 현재 썸네일 추가 =====
            # 현재 시간을 기반으로 랜덤한 문자열 생성
            random_param = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=6)
            )

            if live_info["livePlaybackJson"] != None:

                # JSON 형식의 데이터를 파이썬 딕셔너리로 변환
                live_more_info = json.loads(live_info["livePlaybackJson"])

                # 썸네일 링크 추출
                thumbnail_link = live_more_info["thumbnail"][
                    "snapshotThumbnailTemplate"
                ]

                # URL에 랜덤 파라미터 추가 (동적 Url 생성)
                dynamic_url = thumbnail_link.format(type="480") + "?" + random_param

                # 방송 실시간 이미지 추가
                embed.set_image(url=dynamic_url)
                # =======================================

            # embed 출력
            await interaction.response.send_message(embed=embed, view=view)

        # 2) 현재 라이브 정보가 없으면,
        else:
            # discord에 추가할 embed 생성
            embed = discord.Embed(
                title="치지직에서 현재 쉬고 계신 스트리머의 정보에요!", color=0xFFFFFF
            )
            # embed에 썸네일 사진 (스트리머 사진) 추가
            embed.set_thumbnail(url=channel_info["channelImageUrl"])

            # enbed에 field 추가
            embed.add_field(
                name="스트리머 명", value=channel_info["channelName"], inline=False
            )

            # embed 출력
            await interaction.response.send_message(embed=embed, view=view)
        # ========================================================================================================

    # 에러 처리 (오타 or 치지직에 없는 스트리머 검색 등)
    @chzzk_info.error
    async def chzzk_error(self, interaction: discord.Interaction, error):
        print(error)

        # 사용자가 입력한 값 가져오기
        searched_name = interaction.namespace.채널_이름

        await interaction.response.send_message(
            f"검색하신 **`{searched_name}`** 님은 치지직에 없는 스트리머인 것 같아요...",
        )


async def setup(bot):
    await bot.add_cog(Chzzk(bot))
