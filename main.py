import discord
from discord.ext import commands
import yt_dlp
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Online als {bot.user}")

@bot.command()
async def play(ctx, *, url: str):

    if not ctx.author.voice:
        return await ctx.send("❌ Geh in Voice!")

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if vc is None:
        vc = await channel.connect()
    else:
        await vc.move_to(channel)

    await ctx.send("🎶 Lade...")

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    audio_url = info["url"]

    ffmpeg = discord.FFmpegPCMAudio(
        audio_url,
        executable="/usr/bin/ffmpeg",
        options="-vn"
    )

    if vc.is_playing():
        vc.stop()

    vc.play(ffmpeg)

    await ctx.send("▶️ Spielt: " + info.get("title", "Song"))

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
