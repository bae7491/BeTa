# 디스코드 모듈
import discord
from discord.ext import commands
from discord import app_commands

# API 호출 모듈
import requests

# 날짜 계산 모듈
import pytz
from datetime import datetime, timedelta

# 환경 변수 파일 불러오기를 위해 import.
import os
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()


# ===== 필수 호출 값 (날짜 계산, API 호출) =====
# 1. 메이플 API 불러오기
nexon_api_key = os.getenv("NEXON_OPEN_API_KEY")
headers = {"x-nxopen-api-key": nexon_api_key}

# 메이플 API 호출 url 가져오기
maple_api_url = os.getenv("MAPLE_API_URL")

# 캐릭터 url
# characterUrl = "https://open.api.nexon.com/maplestory/v1/character"
characterUrl = f"{maple_api_url}/character"

# 유니온 url
# unionUrl = "https://open.api.nexon.com/maplestory/v1/user/union"
unionUrl = f"{maple_api_url}/user/union"
# ============================================


# TODO: 캐릭터 식별자 (ocid) 통합하기.
# /maplestory/v1/id | 캐릭터 식별자(ocid) 조회
def get_maple_ocid(nick_name):
    # url = "https://open.api.nexon.com/maplestory/v1/id?character_name=" + 닉네임
    # ocid_response = requests.get(url, headers=headers)

    base_url = f"{maple_api_url}/id"
    params = {"character_name": nick_name}

    ocid_response = requests.get(base_url, headers=headers, params=params)

    return ocid_response


# ===== 메이플 class =====
class Maple(commands.Cog, name="메이플"):
    def __init__(self, bot):
        self.bot = bot

    # 메이플 캐릭터 정보 command
    @app_commands.command(
        name="메이플",
        description="입력한 메이플스토리 캐릭터이름의 정보를 알려드릴게요!",
    )
    @app_commands.describe(닉네임="검색하고 싶은 메이플스토리 닉네임")
    async def maple_info(self, interaction: discord.Interaction, 닉네임: str):
        # 캐릭터 식별자(ocid) 조회 함수 호출
        ocid_response = get_maple_ocid(닉네임)

        # /maplestory/v1/character/basic | 기본 정보 조회
        # JSON 파라미터
        basic_parmas = {
            "ocid": ocid_response.json().get("ocid"),  # 캐릭터 식별자
        }
        basic_response = requests.get(
            f"{characterUrl}/basic", headers=headers, params=basic_parmas
        )

        # /maplestory/v1/character/dojang | 무릉도장 최고 기록 정보 조회
        # JSON 파라미터
        dojang_params = {
            "ocid": ocid_response.json().get("ocid"),  # 캐릭터 식별자
        }
        dojang_response = requests.get(
            f"{characterUrl}/dojang", headers=headers, params=dojang_params
        )

        # /maplestory/v1/user/union | 유니온 정보 조회
        # JSON 파라미터
        unionParams = {
            "ocid": ocid_response.json().get("ocid"),  # 캐릭터 식별자
        }
        unionesponse = requests.get(unionUrl, headers=headers, params=unionParams)

        # discord에 추가할 embed 생성
        embed = discord.Embed(
            title="메이플 월드에 계시는 용사님이에요!",
            description=f"기준 시간 : {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
            color=0xFFFFFF,
        )

        # embed에 썸네일 사진 (캐릭터 이미지) 추가
        embed.set_thumbnail(url=basic_response.json().get("character_image"))

        # embed에 field 추가
        embed.add_field(
            name="닉네임",
            value=basic_response.json().get("character_name"),
            inline=True,
        )
        embed.add_field(
            name="서버", value=basic_response.json().get("world_name"), inline=True
        )
        embed.add_field(
            name="직업", value=basic_response.json().get("character_class"), inline=True
        )
        embed.add_field(
            name="서버", value=basic_response.json().get("world_name"), inline=True
        )
        embed.add_field(
            name="레벨", value=basic_response.json().get("character_level"), inline=True
        )
        embed.add_field(
            name="경험치",
            value=f"{basic_response.json().get('character_exp_rate')} %",
            inline=True,
        )
        embed.add_field(
            name="길드",
            value=basic_response.json().get("character_guild_name"),
            inline=True,
        )
        embed.add_field(
            name="무릉 최고 층수",
            value=f"{dojang_response.json().get('dojang_best_floor')} 층",
            inline=True,
        )
        embed.add_field(
            name="유니온",
            value=format(unionesponse.json().get("union_level"), ","),
            inline=True,
        )

        # NEXON Open API 표기 (이용약관 명시)
        embed.set_footer(text="Data based on NEXON Open API")

        # embed 출력
        await interaction.response.send_message(embed=embed)

    @maple_info.error
    async def maple_info_error(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "메이플 월드에 없는 용사님이신거 같아요..."
        )

    # 메이플 링크 command
    @app_commands.command(
        name="메이플링크",
        description="입력한 메이플스토리 캐릭터이름의 장착 링크 알려드릴게요!",
    )
    @app_commands.describe(
        닉네임="검색하고 싶은 메이플 닉네임",
    )
    async def maple_link(self, interaction: discord.Interaction, 닉네임: str):
        # 캐릭터 식별자(ocid) 조회 함수 호출
        ocid_response = get_maple_ocid(닉네임)

        # /maplestory/v1/character/link-skill | 장착 링크 스킬 정보 조회
        # JSON 파라미터
        link_params = {
            "ocid": ocid_response.json().get("ocid"),  # 캐릭터 식별자
        }
        link_response = requests.get(
            f"{characterUrl}/link-skill", headers=headers, params=link_params
        )

        # ability_response안의 ability_info 빼오기
        link_info_list = link_response.json().get("character_link_skill", [])

        # discord에 추가할 embed 생성
        embed = discord.Embed(
            title=f"{닉네임}의 장착 링크 스킬 정보예요!",
            description=f"기준 시간 : {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
            color=0xFFFFFF,
        )

        # embed에 field 추가
        for link_info in link_info_list:
            embed.add_field(
                name=f'🔹 {link_info.get("skill_name")}',
                value="",
                inline=False,
            )

        # NEXON Open API 표기 (이용약관 명시)
        embed.set_footer(text="Data based on NEXON Open API")

        # embed 출력
        await interaction.response.send_message(embed=embed)

    @maple_link.error
    async def maple_link_error(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "메이플 월드에 없는 용사님이신거 같아요..."
        )

    # 메이플 어빌리티 command
    @app_commands.command(
        name="메이플어빌",
        description="입력한 메이플스토리 캐릭터이름의 어빌리티를 알려드릴게요!",
    )
    @app_commands.describe(닉네임="검색하고 싶은 메이플스토리 닉네임")
    async def maple_ability(self, interaction: discord.Interaction, 닉네임: str):

        # 캐릭터 식별자(ocid) 조회 함수 호출
        ocid_response = get_maple_ocid(닉네임)

        # /maplestory/v1/character/ability | 어빌리티 정보 조회
        # JSON 파라미터
        ability_params = {
            "ocid": ocid_response.json().get("ocid"),  # 캐릭터 식별자
        }
        ability_response = requests.get(
            f"{characterUrl}/ability", headers=headers, params=ability_params
        )

        # ability_response안의 ability_info 빼오기
        ability_info_list = ability_response.json().get("ability_info", [])

        # discord에 추가할 embed 생성
        embed = discord.Embed(
            title=f"{닉네임}의 어빌리티 정보예요!",
            description=f"기준 시간 : {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
            color=0xFFFFFF,
        )

        # embed에 field 추가
        for ability_info in ability_info_list:
            embed.add_field(
                name=f'🔹 {ability_info.get("ability_grade")}',
                value=ability_info.get("ability_value"),
                inline=False,
            )

        # NEXON Open API 표기 (이용약관 명시)
        embed.set_footer(text="Data based on NEXON Open API")

        # embed 출력
        await interaction.response.send_message(embed=embed)

    @maple_ability.error
    async def maple_ability_error(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "메이플 월드에 없는 용사님이신거 같아요..."
        )

    # ==========================


async def setup(bot):
    await bot.add_cog(Maple(bot))
