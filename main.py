import discord
from discord.ext import commands
import yt_dlp
import os

print("🚀 Bot startet...")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"✅ Online als {bot.user}")

# ---------------- PLAY ----------------
@bot.command()
async def play(ctx, *, url: str):

    print("🎵 play command:", url)

    if not ctx.author.voice:
        return await ctx.send("❌ Du musst im Voice Channel sein!")

    channel = ctx.author.voice.channel

    vc = ctx.voice_client

    if vc is None:
        vc = await channel.connect()
    else:
        await vc.move_to(channel)

    await ctx.send("🎶 Lade Musik...")

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        stream_url = info["url"]

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await ctx.send("▶️ Jetzt spielt: " + info.get("title", "Unbekannt"))

    except Exception as e:
        print("❌ ERROR:", e)
        await ctx.send(f"❌ Fehler: {e}")

# ---------------- STOP ----------------
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Gestoppt")

# ---------------- RUN ----------------
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ DISCORD_TOKEN fehlt!")
else:
    bot.run(token)
