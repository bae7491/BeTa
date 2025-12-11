import discord
from discord.ext import commands


class Help(commands.Cog, name="도움"):
    def __init__(self, bot):
        self.bot = bot

    # 도움
    @commands.command(name="도움", help="제가 학습한 것을 알려드릴게요!")
    async def 도움(self, ctx):
        embed = discord.Embed(title="도움말", color=0xFFFFFF)

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1034757143611592757/1034757603798032444/1.png"
        )

        # !도움
        embed.add_field(
            name="!도움", value="```베타가 학습한 것들을 알려드릴게요!```", inline=False
        )

        # 이모티콘
        embed.add_field(
            name="이모티콘 출력",
            value="```이모티콘을 사용하면 확대해서 보여드릴게요!```",
            inline=False,
        )

        # 간단한 커맨드 (SimpleCmd.py)
        embed.add_field(name="간단한 커맨드", value="", inline=False)
        embed.add_field(
            name="(1) !시트",
            value="```TRPG에서 사용하는 시트를 불러드릴게요!```",
            inline=True,
        )
        embed.add_field(name="(2) !ping", value="```pong을 출력.```", inline=True)
        embed.add_field(
            name="(3) !임베드", value="```임베드 사용법을 출력.```", inline=True
        )
        embed.add_field(
            name="(4) !안녕", value="```제가 인사해드릴게요!```", inline=True
        )
        embed.add_field(
            name="(5) !roll",
            value="```1d100다이스를 굴려요. 당신의 SAN치는 어떨까요?```",
            inline=True,
        )
        embed.add_field(
            name="(6) !로또 (숫자)",
            value="```입력한 (숫자)만큼의 로또 번호알려드려요!```",
            inline=True,
        )
        embed.add_field(
            name="(7) !가위바위보",
            value="```저랑 가위바위보 한 판 하실래요?```",
            inline=True,
        )

        # 게임 메이플스토리의 정보 (MapleInfo.py)
        embed.add_field(name="메이플", value="", inline=False)
        embed.add_field(
            name="(1) !메이플 (닉네임)",
            value="```메이플 월드의 유저님을 찾아드려요!```",
            inline=True,
        )
        embed.add_field(
            name="(2) !메이플링크 (닉네임)",
            value="```해당 유저님의 장착 링크를 찾아드려요!```",
            inline=True,
        )
        embed.add_field(
            name="(3) !메이플 (닉네임)",
            value="```해당 유저님의 어빌리티를 찾아드려요!```",
            inline=True,
        )

        # 디스코드 채널 영혼들의 안식처의 게임 메이플스토리 파티 정보 (MapleParty.py)
        embed.add_field(name="파티", value="", inline=False)
        embed.add_field(
            name="(1) !파티 등록 (보스이름) (유저이름1 유저이름2)",
            value="```영혼방의 메이플 파티 정보를 베타가 기록할게요!```",
            inline=True,
        )
        embed.add_field(
            name="(2) !파티 조회 보스 (보스이름)",
            value="``제가 기록한 영혼방의 메이플 파티 정보를 보스 이름 기준으로 알려드릴게요!```",
            inline=True,
        )
        embed.add_field(
            name="(3) !파티 조회 캐릭터 (유저이름)",
            value="``제가 기록한 영혼방의 메이플 파티 정보를 유저님의 이름을 기준으로 알려드릴게요!```",
            inline=True,
        )

        # 날씨 정보 (Weather.py)
        embed.add_field(name="날씨", value="", inline=False)
        embed.add_field(
            name="(1) !날씨 (도시이름)",
            value="```입력한 도시의 현재 날씨를 검색해드려요!```",
        )

        # # 버스 정보 (Bus.py)
        # embed.add_field(
        #     name="(1) !부산버스 (버스 번호) (정류장 이름)",
        #     value="```부산의 원하는 (버스 번호)가 정차하는 (정류장 이름)이 있는지 찾아드려요!```",
        #     inline=True,
        # )
        # embed.add_field(
        #     name="(2) 부산버스 명령어 이후 -> !정류장 (숫자)",
        #     value="```!부산버스 명령어로 찾은 정류장의 번호를 입력하면 버스가 언제 도착하는지 정보를 알려드려요!```",
        # )
        # embed.add_field(
        #     name="(3) !양산버스 (버스 번호) (정류장 이름)",
        #     value="```양산의 원하는 (버스 번호)가 정차하는 (정류장 이름)이 있는지 찾아드려요!```",
        #     inline=True,
        # )
        # embed.add_field(
        #     name="(4) 양산버스 명령어 이후 -> !정류장 (숫자)",
        #     value="```!양산버스 명령어로 찾은 정류장의 번호를 입력하면 버스가 언제 도착하는지 정보를 알려드려요!```",
        # )

        # embed 출력
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
