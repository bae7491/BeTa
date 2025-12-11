# 디스코드 모듈
import discord
from discord.ext import commands
from discord import app_commands

# API 호출 모듈
import requests, json

# 날짜 계산 모듈
import pytz
from datetime import datetime

# 환경 변수 파일 불러오기를 위해 import.
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


# ===== 필수 호출 값 (날짜 계산, API 호출) =====
# === parameter ===
# 1. Kakao API Key
KAKAO_OPEN_API_KEY = os.getenv("KAKAO_OPEN_API_KEY")
kakao_headers = {"Authorization": f"KakaoAK {KAKAO_OPEN_API_KEY}"}

# 2. OpenWeatherMap API Key
weather_api_key = os.getenv("OPEN_WEATHER_MAP_OPEN_API_KEY")
# ================


# === function ===
# 1. 카카오 API 호출 (function / 위, 경도 계산)
def get_location(location):
    base_url = os.getenv("KAKAO_API_URL")
    params = {"query": location}

    kakao_response = requests.get(base_url, headers=kakao_headers, params=params)

    address = kakao_response.json()["documents"][0]["address"]

    # 검색 주소 변수 저장
    search_addr = {"address_name": str(address["address_name"])}

    # 위, 경도 json
    coordinates = {"lat": str(address["y"]), "lng": str(address["x"])}

    return search_addr, coordinates


# 2. OpenWeatherMap API 호출 (function)
def get_weather(lat, lng):
    base_url = os.getenv("OPEN_WEATHER_MAP_API_URL")
    params = {
        "lat": lat,
        "lon": lng,
        "appid": weather_api_key,
        "lang": "kr",
        "units": "metric",
    }

    weather_response = requests.get(base_url, params=params)

    return weather_response


# =========================


# ===== Weather class =====
class Weather(commands.Cog, name="날씨"):
    def __init__(self, bot):
        self.bot = bot

    # 현재 날씨 정보 command
    @app_commands.command(name="날씨", description="입력한 지역의 날씨를 알려드릴게요!")
    @app_commands.describe(지역_이름="날씨를 알고 싶은 지역 이름")
    async def weather(self, interaction: discord.Interaction, 지역_이름: str):

        # 위, 경도 구하기
        search_info = get_location(지역_이름)
        search_addr = search_info[0]
        coordinates = search_info[1]

        # 위, 경도를 이용해 그 좌표의 날씨 구하기
        weather_info = json.loads(
            get_weather(coordinates["lat"], coordinates["lng"]).text
        )

        # discord에 추가할 embed 생성
        embed = discord.Embed(
            title=f"{search_addr['address_name']}의 날씨예요!",
            timestamp=datetime.now(pytz.timezone("UTC")),
            color=0xFFFFFF,
        )

        # embed에 썸네일 사진 (캐릭터 이미지) 추가
        embed.set_thumbnail(
            url=f"http://openweathermap.org/img/wn/{weather_info['weather'][0]['icon']}.png"
        )

        # embed에 field 추가
        embed.add_field(
            name="현재 온도",
            value=f"{round(weather_info['main']['temp'], 1)} ℃",
            inline=True,
        )
        embed.add_field(
            name="체감 온도",
            value=f"{round(weather_info['main']['feels_like'], 1)} ℃",
            inline=True,
        )
        if "rain" in weather_info:
            embed.add_field(
                name="강수량(mm)", value=f"{weather_info['rain']['1h']} mm", inline=True
            )
        if "snow" in weather_info:
            embed.add_field(
                name="적설량(mm)", value=f"{weather_info['snow']['1h']} mm", inline=True
            )
        embed.add_field(
            name="습도", value=f"{weather_info['main']['humidity']} %", inline=True
        )

        # embed 출력
        await interaction.response.send_message(embed=embed)

    @weather.error
    async def weather_error(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message("제가 모르는 지역인 것 같아요...")


# ==========================


async def setup(bot):
    await bot.add_cog(Weather(bot))
