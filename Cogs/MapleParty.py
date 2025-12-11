import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

import json
import os
import functools

# 환경 변수 파일 불러오기를 위해 import.
import os
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()

# .env의 MAPLE_PARTY_DATA_PATH을 참고.
PARTY_DATA_FILE = os.getenv("MAPLE_PARTY_DATA_PATH")


# =====================================================================================================
# 메이플 파티 json 파일 관련 함수
# JSON 파일 로드
def load_data():
    if os.path.exists(PARTY_DATA_FILE):
        with open(PARTY_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# JSON 파일 저장
def save_data(data):
    with open(PARTY_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 파티 데이터 불러와 변수로 저장
party_data = load_data()
# =====================================================================================================


# =====================================================================================================
# 명령어 (메이플_파티_조회) 관련 함수 / 클래스
# 명령어 (메이플_파티_조회) 사용 시, 보스 이름을 기준으로 파티 목록 임베드 생성 함수
def create_boss_embed(boss_name):
    """보스별 파티 목록을 생성하는 임베드"""
    embed = discord.Embed(title=f"🛡 {boss_name} 파티 정보", color=0xFFFFFF)

    parties = party_data.get(boss_name, [])

    if not parties:  # 저장된 파티가 없는 경우
        embed.add_field(
            name="⚠️ 파티 정보 없음",
            value="해당 보스에 등록된 파티 정보가 없어요!",
            inline=False,
        )
    else:
        for i, party in enumerate(parties):
            embed.add_field(name=f"🔹 파티 {i+1}", value=", ".join(party), inline=False)

    return embed


# 명령어 (메이플_파티_조회) 사용 시, 캐릭터 이름을 기준으로 파티 목록 임베드 생성 함수
def create_character_embed(character_name):
    """캐릭터별 보스 및 파티 정보를 생성하는 임베드"""
    embed = discord.Embed(
        title=f"🔍 `{character_name}`의 메이플 파티 정보예요!", color=0xFFFFFF
    )
    for boss, parties in party_data.items():
        for i, party in enumerate(parties):
            if character_name in party:
                embed.add_field(name=f"🔹 {boss}", value=", ".join(party), inline=False)
    return embed


# 명령어 (메이플_파티_조회) 사용 시, 캐릭터 이름을 입력받기 위한 모달 클래스
class CharacterInputModal(discord.ui.Modal, title="캐릭터 검색"):
    """캐릭터 입력을 위한 모달"""

    name = discord.ui.TextInput(
        label="캐릭터 이름",
        placeholder="검색할 캐릭터 이름을 입력하세요",
        required=True,
    )

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """입력된 캐릭터가 포함된 보스 및 파티 목록을 출력"""
        character_name = self.name.value.strip()

        embed = discord.Embed(
            title=f"🔍 `{character_name}`의 보스 및 파티 정보", color=0xFFFFFF
        )
        found = False

        for boss, parties in party_data.items():
            for i, party in enumerate(parties):
                if character_name in party:
                    embed.add_field(
                        name=f"🔹 {boss}",
                        value=", ".join(party),
                        inline=False,
                    )
                    found = True

        if found:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"⚠️ `{character_name}`님은 등록되지 않은 용사님이예요...",
                ephemeral=True,
            )


# =====================================================================================================


# =====================================================================================================
# 명령어 (메이플_파티_삭제) 관련 함수 / 클래스
# 명령어 (메이플_파티_삭제) 사용 시, 보스 이름을 기준으로 생성한 임베드에 삭제 버튼 추가 함수
def create_boss_embed_with_delete_buttons(boss_name):
    """보스별 파티 목록을 생성하며 삭제 버튼 추가"""
    embed = discord.Embed(title=f"🛡 {boss_name} 파티 삭제", color=0xFFFFFF)
    view = discord.ui.View()

    parties = party_data.get(boss_name, [])

    if not parties:  # 저장된 파티가 없는 경우
        embed.add_field(
            name="⚠️ 파티 정보 없음", value="등록된 파티가 없어요!", inline=False
        )
        return embed, None  # 버튼이 필요 없으므로 View를 None으로 반환

    for i, party in enumerate(parties):
        embed.add_field(name=f"🔹 파티 {i+1}", value=", ".join(party), inline=False)

        button = discord.ui.Button(
            label=f"파티 {i+1} 삭제", style=discord.ButtonStyle.danger
        )

        async def delete_callback(
            interaction: discord.Interaction, index=i, boss=boss_name
        ):
            if boss in party_data and 0 <= index < len(party_data[boss]):
                deleted_party = party_data[boss].pop(index)
                save_data(party_data)

                if not party_data[boss]:  # 모든 파티가 삭제되었을 경우
                    updated_embed, _ = create_boss_embed_with_delete_buttons(boss)
                    await interaction.response.edit_message(
                        embed=updated_embed, view=None
                    )
                else:
                    updated_embed, updated_view = create_boss_embed_with_delete_buttons(
                        boss
                    )
                    await interaction.response.edit_message(
                        embed=updated_embed, view=updated_view
                    )

        button.callback = delete_callback
        view.add_item(button)

    return embed, view


# # 명령어 (메이플_파티_삭제) 사용 시, 보스 이름을 기준으로 삭제 임베드를 불러오는 함수
def create_delete_view(boss_name):
    """삭제 버튼이 포함된 View 생성"""
    embed, view = create_boss_embed_with_delete_buttons(boss_name)
    return view


# 명령어 (메이플_파티_삭제) 사용 시, 보스 이름을 기준으로 조회한 임베드에 삭제 기능을 수행할 함수
def create_boss_embed_with_delete_buttons(boss_name):
    """보스별 파티 목록을 생성하며 삭제 버튼 추가"""
    embed = discord.Embed(title=f"🛡 {boss_name} 파티 삭제", color=0xFFFFFF)
    view = discord.ui.View()

    parties = party_data.get(boss_name, [])

    if not parties:  # 저장된 파티가 없는 경우
        embed.add_field(
            name="⚠️ 파티 정보 없음",
            value="해당 용사님이 등록된 파티가 없어요!",
            inline=False,
        )
    else:
        for i, party in enumerate(parties):
            embed.add_field(name=f"🔹 파티 {i+1}", value=", ".join(party), inline=False)

            button = discord.ui.Button(
                label=f"파티 {i+1} 삭제", style=discord.ButtonStyle.danger
            )

            async def delete_callback(
                interaction: discord.Interaction, index=i, boss=boss_name
            ):
                if boss in party_data and 0 <= index < len(party_data[boss]):
                    deleted_party = party_data[boss].pop(index)
                    save_data(party_data)

                    if not party_data[boss]:  # 모든 파티가 삭제되었을 경우
                        await interaction.response.edit_message(
                            content=f"🚫 `{boss}`의 모든 파티 정보를 삭제했어요!",
                            embed=None,
                            view=None,
                        )
                    else:
                        updated_embed, updated_view = (
                            create_boss_embed_with_delete_buttons(boss)
                        )
                        await interaction.response.edit_message(
                            embed=updated_embed, view=updated_view
                        )

            button.callback = delete_callback
            view.add_item(button)

    return embed, view


# 명령어 (메이플_파티_삭제) 사용 시, 캐릭터 이름을 기준으로 조회한 임베드에 삭제 기능을 수행할 함수
def create_character_embed_with_delete_buttons(character_name):
    """캐릭터 기준으로 보스별 파티 삭제 버튼을 포함한 임베드 생성"""
    embed = discord.Embed(title=f"🛡 `{character_name}`의 파티 삭제", color=0xFFFFFF)
    view = discord.ui.View()
    found = False

    for boss, parties in party_data.items():
        for i, party in enumerate(parties):
            if character_name in party:
                embed.add_field(
                    # name=f"🛡 {boss} - 파티 {i+1}", value=", ".join(party), inline=False
                    name=f"🛡 {boss} - 파티",
                    value=", ".join(party),
                    inline=False,
                )
                found = True

                button = discord.ui.Button(
                    # label=f"{boss} - 파티 {i+1} 삭제", style=discord.ButtonStyle.danger
                    label=f"{boss} - 파티 삭제",
                    style=discord.ButtonStyle.danger,
                )

                async def delete_callback(
                    interaction: discord.Interaction, boss_name=boss, index=i
                ):
                    """파티 삭제 후 임베드를 업데이트하는 콜백"""
                    if boss_name in party_data and 0 <= index < len(
                        party_data[boss_name]
                    ):
                        party_data[boss_name].pop(index)
                        save_data(party_data)

                    # 변경된 데이터를 반영하여 새로운 임베드와 버튼 생성
                    updated_embed, updated_view = (
                        create_character_embed_with_delete_buttons(character_name)
                    )
                    await interaction.response.edit_message(
                        embed=updated_embed, view=updated_view
                    )

                # functools.partial을 사용하여 각 버튼에 고유한 콜백 전달
                button.callback = functools.partial(delete_callback)
                view.add_item(button)

    if not found:
        embed.add_field(
            name="⚠️ 삭제할 파티 없음",
            value="이 캐릭터가 포함된 파티가 없어요!",
            inline=False,
        )
        view.clear_items()  # 삭제할 파티가 없으면 버튼 제거

    return embed, view


# 명령어 (메이플_파티_삭제) 사용 시, 삭제 임베드를 불러오기 위해 캐릭터 이름을 입력받는 모달 클래스
class CharacterDeleteInputModal(discord.ui.Modal, title="캐릭터 파티 삭제"):
    """캐릭터 파티 삭제를 위한 모달"""

    name = discord.ui.TextInput(
        label="캐릭터 이름",
        placeholder="삭제할 캐릭터 이름을 입력하세요",
        required=True,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """입력된 캐릭터가 포함된 보스 및 파티 목록을 출력하고 삭제 버튼 추가"""
        character_name = self.name.value.strip()
        embed, view = create_character_embed_with_delete_buttons(character_name)

        await interaction.response.send_message(embed=embed, view=view)


# =====================================================================================================


# =====================================================================================================
# 명령어 메이플_파티에 대한 클래스
class Party(commands.Cog, name="파티 관리"):
    """명령어 메이플_파티 클래스"""

    def __init__(self, bot):
        self.bot = bot

    # =====================================================================================================
    # ✅ 파티 등록
    @app_commands.command(
        name="메이플_파티_등록",
        description="영혼들의 안식처의 메이플 보스 파티에 정보를 등록해드려요!",
    )
    @app_commands.describe(
        보스_이름="등록할 보스 이름",
        파티원_이름="등록할 파티원의 이름(쉼표로 구분)",
    )
    # JSON 파일에서 보스 이름 동적으로 가져오기
    @app_commands.choices(
        보스_이름=[Choice(name=boss, value=boss) for boss in party_data.keys()]
    )
    async def register_maple_party(
        self,
        interaction: discord.Interaction,
        보스_이름: app_commands.Choice[str],
        파티원_이름: str,
    ):
        """메이플 파티 등록 기능 함수"""
        new_party = [
            member.strip() for member in 파티원_이름.split(",") if member.strip()
        ]

        # 해당 보스에 이미 동일한 파티원이 존재하는지 확인
        for existing_party in party_data[보스_이름.value]:
            if set(existing_party) & set(new_party):  # 하나라도 겹치면 등록 불가
                await interaction.response.send_message(
                    f"❌ `{보스_이름.value}`에 이미 등록된 파티원이 포함되어 있어요..."
                )
                return

        # 파티 등록
        party_data[보스_이름.value].append(new_party)
        save_data(party_data)
        await interaction.response.send_message(
            f"✅ `{보스_이름.value}`에 파티 `{', '.join(new_party)}` 등록했어요!"
        )

    # =====================================================================================================

    # =====================================================================================================
    # ✅ 파티 조회
    @app_commands.command(
        name="메이플_파티_조회",
        description="영혼들의 안식처의 메이플 보스 파티에서 원하는 파티 정보를 찾아드려요!",
    )
    @app_commands.describe(
        카테고리="(보스) or (캐릭터) 중 조회하고 싶은 카테고리",
    )
    @app_commands.choices(
        카테고리=[
            app_commands.Choice(name="보스", value="보스"),
            app_commands.Choice(name="캐릭터", value="캐릭터"),
        ]
    )
    async def query_maple_party(
        self,
        interaction: discord.Interaction,
        카테고리: app_commands.Choice[str],
    ):
        """보스 또는 캐릭터 기준으로 파티를 조회하는 명령어"""
        if 카테고리.value == "보스":
            boss_list = party_data.keys()
            options = [
                discord.SelectOption(label=boss, value=boss) for boss in boss_list
            ]

            if not options:
                await interaction.response.send_message(
                    "❌ 등록된 보스 정보가 없어요...", ephemeral=True
                )
                return

            select = discord.ui.Select(
                placeholder="파티를 조회할 보스 이름을 선택해주세요!", options=options
            )

            async def select_callback(interaction: discord.Interaction):
                boss_name = select.values[0]
                embed = create_boss_embed(boss_name)

                # View에서 Select 제거 후 메시지 수정
                view.clear_items()
                await interaction.response.edit_message(embed=embed, view=view)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view)
        elif 카테고리.value == "캐릭터":
            await interaction.response.send_modal(
                CharacterInputModal(bot=interaction.client)
            )

    # =====================================================================================================

    # =====================================================================================================
    # ✅ 파티 삭제
    @app_commands.command(
        name="메이플_파티_삭제",
        description="영혼들의 안식처의 메이플 보스 파티에서 원하는 파티를 삭제해드려요!",
    )
    @app_commands.describe(
        카테고리="(보스) or (캐릭터) 중 삭제하고 싶은 카테고리",
    )
    @app_commands.choices(
        카테고리=[
            app_commands.Choice(name="보스", value="보스"),
            app_commands.Choice(name="캐릭터", value="캐릭터"),
        ]
    )
    async def delete_maple_party(
        self, interaction: discord.Interaction, 카테고리: app_commands.Choice[str]
    ):
        """보스 또는 캐릭터 기준으로 파티를 삭제하는 명령어"""
        if 카테고리.value == "보스":
            boss_list = party_data.keys()
            options = [
                discord.SelectOption(label=boss, value=boss) for boss in boss_list
            ]

            if not options:
                await interaction.response.send_message(
                    "❌ 삭제할 보스 정보가 없어요...", ephemeral=True
                )
                return

            select = discord.ui.Select(
                placeholder="파티를 삭제할 보스 이름을 선택해주세요!", options=options
            )

            async def select_callback(interaction: discord.Interaction):
                boss_name = select.values[0]
                embed, view = create_boss_embed_with_delete_buttons(boss_name)

                # Select만 제거하고 삭제 버튼은 유지
                for item in view.children:
                    if isinstance(item, discord.ui.Select):
                        view.remove_item(item)

                await interaction.response.edit_message(embed=embed, view=view)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(view=view)

        elif 카테고리.value == "캐릭터":
            await interaction.response.send_modal(
                CharacterDeleteInputModal(bot=interaction.client)
            )

    # =====================================================================================================
    # 명령어 관련 에러 처리

    # 명령어 (메이플_파티_등록) 에러 처리
    @register_maple_party.error
    async def registerPartyError(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "파티 등록 명령어가 잘못된 것 같아요..."
        )

    # 명령어 (메이플_파티_등록) 에러 처리
    @query_maple_party.error
    async def queryMapleParty(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "파티 조회 명령어가 잘못된 것 같아요..."
        )

    # 명령어 (메이플_파티_등록) 에러 처리
    @delete_maple_party.error
    async def deleteMapleParty(self, interaction: discord.Interaction, error):
        print(error)
        await interaction.response.send_message(
            "파티 삭제 명령어가 잘못된 것 같아요..."
        )


# =====================================================================================================


async def setup(bot):
    await bot.add_cog(Party(bot))
