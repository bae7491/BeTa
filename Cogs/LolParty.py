import discord
from discord.ext import commands
from discord import app_commands
import random


class LolParty(commands.Cog, name="롤 랜덤 파티"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="롤파티", description="유저 5명을 입력받아 무작위로 라인 배정"
    )
    @app_commands.describe(
        유저1="롤파티에 추가할 첫번째 유저",
        유저2="롤파티에 추가할 두번째 유저",
        유저3="롤파티에 추가할 세번째 유저",
        유저4="롤파티에 추가할 네번째 유저",
        유저5="롤파티에 추가할 다섯번째 유저",
    )
    async def lol_party(
        self,
        interaction: discord.Interaction,
        유저1: str,
        유저2: str,
        유저3: str,
        유저4: str,
        유저5: str,
    ):
        users = [유저1, 유저2, 유저3, 유저4, 유저5]
        roles = ["탑", "정글", "미드", "원딜", "서폿"]
        random.shuffle(users)

        embed = discord.Embed(title="🎮 롤 랜덤 라인 배정", color=0xFFFFFF)
        for user, role in zip(users, roles):
            embed.add_field(name=role, value=f"{user}", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(LolParty(bot))
