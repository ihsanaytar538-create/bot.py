import discord
from discord.ext import commands
import yt_dlp
import re

TOKEN = "DEIN_DISCORD_TOKEN"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# YTDL SETUP
# -------------------------
ytdl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

queue = []


# -------------------------
# SEARCH / EXTRACT
# -------------------------
def get_source(query):
    info = ytdl.extract_info(query, download=False)

    if "entries" in info:
        info = info["entries"][0]

    return info["url"], info["title"]


# -------------------------
# JOIN VOICE
# -------------------------
async def join_voice(ctx):
    if ctx.author.voice is None:
        await ctx.send("❌ Du bist in keinem Voice Channel")
        return None

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        return await channel.connect()
    else:
        return ctx.voice_client


# -------------------------
# PLAY NEXT IN QUEUE
# -------------------------
async def play_next(ctx):
    if len(queue) == 0:
        return

    url = queue.pop(0)
    voice = ctx.voice_client

    stream_url, title = get_source(url)

    source = await discord.FFmpegOpusAudio.from_probe(
        stream_url,
        **ffmpeg_opts
    )

    voice.play(source, after=lambda e: bot.loop.create_task(play_next(ctx)))


# -------------------------
# COMMAND: PLAY
# -------------------------
@bot.command()
async def play(ctx, *, query):
    voice = await join_voice(ctx)
    if voice is None:
        return

    # Spotify Link → nur als Suchquery nutzen
    spotify_match = re.search(r"track/([a-zA-Z0-9]+)", query)
    if spotify_match:
        query = f"ytsearch:{query}"

    queue.append(query)

    if not voice.is_playing():
        await play_next(ctx)

    await ctx.send(f"🎵 Hinzugefügt zur Queue: `{query}`")


# -------------------------
# SKIP
# -------------------------
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Skip")


# -------------------------
# STOP
# -------------------------
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⛔ Stopped + Queue geleert")


# -------------------------
# LEAVE
# -------------------------
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


# -------------------------
# READY
# -------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")


bot.run(TOKEN)
