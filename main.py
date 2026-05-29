import discord
from discord.ext import commands
import yt_dlp
import os

# ---------------- INTENTS ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"✅ Online als {bot.user}")

# ---------------- TEST ----------------
@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot funktioniert!")

# ---------------- PLAY ----------------
@bot.command()
async def play(ctx, *, url: str):

    if not ctx.author.voice:
        return await ctx.send("❌ Du musst in einem Voice Channel sein!")

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    try:
        # Connect / Move
        if vc is None:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        await ctx.send("🔄 Lade Musik...")

        # yt-dlp
        ydl_opts = {
            "format": "bestaudio[ext=webm]/bestaudio/best",
            "noplaylist": True,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # stabiler Audio Stream
        audio_url = None
        for f in info.get("formats", []):
            if f.get("acodec") != "none" and f.get("url"):
                audio_url = f["url"]
                break

        if not audio_url:
            return await ctx.send("❌ Kein Audio gefunden")

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10",
            "options": "-vn"
        }

        # 🔥 WICHTIG: absoluter ffmpeg Pfad (Railway Fix)
        source = discord.FFmpegPCMAudio(
            audio_url,
            executable="/usr/bin/ffmpeg",
            **ffmpeg_options
        )

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await ctx.send(f"🎶 Jetzt spielt: {info.get('title', 'Unbekannt')}")

    except Exception as e:
        print("PLAY ERROR:", e)
        await ctx.send(f"❌ Fehler: {e}")

# ---------------- STOP ----------------
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Gestoppt")

# ---------------- START ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
