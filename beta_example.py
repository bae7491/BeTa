import traceback
import re
import sys
import os
import asyncio
import discord
from discord.ext import commands

from datetime import datetime, timedelta


# 봇 트리거 설정.
bot = commands.Bot(command_prefix="@", intents=discord.Intents.all())


# 봇 입장 시.
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    game = discord.Game("딥러닝 중")
    await bot.change_presence(status=discord.Status.online, activity=game)

    # ✅ 슬래시 커맨드 동기화 추가
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)}개의 슬래시 커맨드가 동기화되었습니다.")
    except Exception as e:
        print(f"❌ 슬래시 커맨드 동기화 실패: {e}")


# Cogs로 Cogs폴더 내의 다른 py 파일 로드.
async def load():
    for file in os.listdir("Cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"Cogs.{file[:-3]}")


# !rank 명령어 무시.
@bot.command()
async def rank(ctx):
    if ctx.author != bot.user:
        return


# 이모티콘.
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if not message.guild or message.author.id == bot.user.id:
        return

    if m := re.match(r"^<a?:[\w]+:([\d]+)>$", message.content):
        if message.content.startswith("<a:"):
            ext = "gif"
        else:
            ext = "png"

        embed = discord.Embed(color=message.author.color)
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar
        )
        embed.set_image(url=f"https://cdn.discordapp.com/emojis/{m.group(1)}.{ext}")

        await bot.process_commands(message)
        await message.channel.send(
            embed=embed, reference=message.reference, mention_author=True
        )
        await message.delete()


# 나머지 입력 시.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send("무슨소리인지 잘 모르겠어요...")
        return
    else:
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )


# main().
async def main():
    await load()

    # 봇 토큰 입력.
    await bot.start("YOUR_BOT_TOKEN_HERE")


asyncio.run(main())
