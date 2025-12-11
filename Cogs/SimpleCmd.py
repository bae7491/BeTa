import discord
from discord.ext import commands
from discord import app_commands
import random
import numpy

# embed에 현재 시간 출력을 위해 import.
import datetime
import pytz

# 환경 변수 파일 불러오기를 위해 import.
import os
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()


class SimpleCmd(commands.Cog, name="간단한 커맨드"):
    def __init__(self, bot):
        self.bot = bot

    # 핑퐁.
    @app_commands.command(name="ping", description="저와 '핑퐁'하실래요?")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

    # hello.
    @app_commands.command(name="안녕", description="저와 인사하실래요?")
    async def hello(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0xFFFFFF)
        embed.set_image(
            # 베타 이미지 URL
            url=os.getenv("HELLO_CHRISTMAS_BETA_IMAGE_URL")
        )
        await interaction.response.send_message(embed=embed)

    # TRPG 시트 불러오기.
    @app_commands.command(
        name="시트", description="TRPG 시트가 있는 드라이브 폴더를 불러올게요!"
    )
    async def trpg_sheet(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="TRPG 캐릭터 모음 시트",
            url=os.getenv("TRPG_EXTERNAL_URL"),
            description="TRPG 캐릭터 시트가 있는 드라이브 폴더에요!\n(클릭시 이동.)",
            color=0xFFFFFF,
        )
        await interaction.response.send_message(embed=embed)

    # 주사위 roll.
    @app_commands.command(name="roll", description="1d100 주사위를 돌려드릴게요!")
    async def roll(self, interaction: discord.Interaction):
        await interaction.response.send_message("주사위를 굴릴게요!")
        range = random.randint(1, 100)
        embed = discord.Embed(title="1d100의 결과는?", color=0xFFFFFF)
        embed.add_field(name="결과", value=range)
        await interaction.followup.send(embed=embed)

    # 로또 번호 추첨.
    @app_commands.command(name="로또", description="로또 번호를 추천해드릴게요!")
    @app_commands.describe(횟수="뽑고 싶은 로또 횟수")
    async def lotto(self, interaction: discord.Interaction, 횟수: int):
        embed = discord.Embed(
            title="로또 번호 추첨",
            timestamp=datetime.datetime.now(pytz.timezone("UTC")),
            color=0xFFFFFF,
        )

        for i in range(횟수):
            lotto_num = []

            for j in range(6):
                lotto_num = numpy.random.choice(range(1, 46), 6, replace=False)

            lotto_num.sort()
            embed.add_field(
                name="결과", value=f"{i+1}. 로또번호 : {lotto_num}", inline=False
            )

        await interaction.response.send_message(embed=embed)

    # 가위바위보 기능.
    @app_commands.command(
        name="가위바위보",
        description="저와 가위바위보 한 판 하실래요?",
    )
    @app_commands.describe(선택="가위, 바위, 보 중에 선택")
    @app_commands.choices(
        선택=[
            app_commands.Choice(name="가위", value="가위"),
            app_commands.Choice(name="바위", value="바위"),
            app_commands.Choice(name="보", value="보"),
        ]
    )
    async def rock_scissors_paper(
        self, interaction: discord.Interaction, 선택: app_commands.Choice[str]
    ):
        # 가위바위보 리스트
        rspList = ["가위", "바위", "보"]

        # 가위바위보 리스트에서 무작위 값 하나 가져오기
        betaChoice = random.choice(rspList)

        if 선택.value == "가위":
            pickEmoji = "✌️"
            if betaChoice == "가위":
                betaEmoji = "✌️"
                result = "비겼어요...😓"
            elif betaChoice == "바위":
                betaEmoji = "✊"
                result = "제가 이겼네요! 😆"
            else:
                betaEmoji = "✋"
                result = "제가 졌어요... 😫"

        if 선택.value == "바위":
            pickEmoji = "✊"
            if betaChoice == "바위":
                betaEmoji = "✊"
                result = "비겼어요...😓"
            elif betaChoice == "보":
                betaEmoji = "✋"
                result = "제가 이겼네요! 😆"
            else:
                betaEmoji = "✌️"
                result = "제가 졌어요... 😫"

        if 선택.value == "보":
            pickEmoji = "✋"
            if betaChoice == "보":
                betaEmoji = "✋"
                result = "비겼어요...😓"
            elif betaChoice == "가위":
                betaEmoji = "✌️"
                result = "제가 이겼네요! 😆"
            else:
                betaEmoji = "✊"
                result = "제가 졌어요... 😫"

        embed = discord.Embed(title="가위바위보 결과", color=0xFFFFFF)
        embed.add_field(
            name=f"{interaction.user.display_name} 님",
            value=f"{pickEmoji} ({선택.value})",
            inline=False,
        )
        embed.add_field(name="베타", value=f"{betaEmoji} ({betaChoice})", inline=False)
        embed.add_field(name="결과", value=result, inline=False)
        await interaction.response.send_message(embed=embed)

    @lotto.error
    async def lotto_error(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "!로또 (숫자) 를 잘못 입력하신 것 같아요..."
        )


async def setup(bot):
    await bot.add_cog(SimpleCmd(bot))
