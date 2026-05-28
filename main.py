import discord
from discord.ext import commands
import yt_dlp

TOKEN = "DEIN_DISCORD_TOKEN"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
current = None

ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)


# -------------------------
# AUDIO FETCH
# -------------------------
def get_audio(query):
    info = ytdl.extract_info(f"ytsearch:{query}", download=False)
    info = info["entries"][0]
    return info["url"], info["title"]


# -------------------------
# EMBED UI
# -------------------------
async def now_playing(ctx, title):
    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**{title}**",
        color=0x1DB954
    )
    await ctx.send(embed=embed)


# -------------------------
# PLAY NEXT
# -------------------------
async def play_next(ctx):
    global current

    if len(queue) == 0:
        current = None
        return

    current = queue.pop(0)

    url, title = get_audio(current)

    voice = ctx.voice_client

    source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_opts)

    def after_playing(error):
        bot.loop.create_task(play_next(ctx))

    voice.play(source, after=after_playing)

    await now_playing(ctx, title)


# -------------------------
# JOIN
# -------------------------
async def join(ctx):
    if ctx.author.voice is None:
        return None

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        return await channel.connect()

    return ctx.voice_client


# -------------------------
# PLAY COMMAND
# -------------------------
@bot.command()
async def play(ctx, *, query):
    voice = await join(ctx)
    if voice is None:
        await ctx.send("❌ Du bist nicht im Voice Channel")
        return

    queue.append(query)

    if not voice.is_playing():
        await play_next(ctx)
    else:
        await ctx.send("➕ Zur Queue hinzugefügt")


# -------------------------
# CONTROL COMMANDS
# -------------------------
@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏭ Skip")


@bot.command()
async def pause(ctx):
    if ctx.voice_client:
        ctx.voice_client.pause()
        await ctx.send("⏸ Paused")


@bot.command()
async def resume(ctx):
    if ctx.voice_client:
        ctx.voice_client.resume()
        await ctx.send("▶ Resumed")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⛔ Stopped")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


# -------------------------
# START
# -------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN)
