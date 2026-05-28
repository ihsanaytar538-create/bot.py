import discord
from discord.ext import commands
import yt_dlp
import re
import os

# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# QUEUE
# =========================
queue = []
current = None

# =========================
# YT-DLP SETTINGS
# =========================
ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ydl_opts)

# =========================
# EXTRACT AUDIO
# =========================
def get_audio(query):
    info = ytdl.extract_info(f"ytsearch:{query}", download=False)
    if "entries" in info:
        info = info["entries"][0]
    return info["url"], info["title"]

# =========================
# VOICE JOIN
# =========================
async def join_voice(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ Du bist in keinem Voice Channel")
        return None

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        return await channel.connect()

    return ctx.voice_client

# =========================
# PLAY NEXT
# =========================
async def play_next(ctx):
    global current

    if len(queue) == 0:
        current = None
        return

    current = queue.pop(0)

    url, title = get_audio(current)
    voice = ctx.voice_client

    source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_opts)

    def after(error):
        bot.loop.create_task(play_next(ctx))

    voice.play(source, after=after)

    await ctx.send(f"🎵 Now Playing: **{title}**")

# =========================
# PLAY COMMAND
# =========================
@bot.command()
async def play(ctx, *, query):
    voice = await join_voice(ctx)
    if not voice:
        return

    # Spotify Link Support
    match = re.search(r"track/([a-zA-Z0-9]+)", query)
    if match:
        query = f"spotify track {match.group(1)}"

    queue.append(query)

    if not voice.is_playing():
        await play_next(ctx)
    else:
        await ctx.send("➕ Zur Queue hinzugefügt")

# =========================
# SKIP
# =========================
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Skip")

# =========================
# STOP
# =========================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⛔ Stopped")

# =========================
# LEAVE
# =========================
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

# =========================
# RUN
# =========================
bot.run(TOKEN)
