import discord
from discord.ext import commands
import yt_dlp
import os

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
        # connect / move
        if vc is None:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        await ctx.send("🔄 Lade Musik...")

        # 🔥 STABILER YT-DLP FIX
        with yt_dlp.YoutubeDL({
            "format": "bestaudio[ext=webm]/bestaudio/best",
            "noplaylist": True,
            "quiet": True
        }) as ydl:
            info = ydl.extract_info(url, download=False)

        # 🔥 WICHTIG: stabiler Audio-Stream
        audio_url = None

        for f in info["formats"]:
            if f.get("acodec") != "none":
                audio_url = f["url"]
                break

        if audio_url is None:
            return await ctx.send("❌ Kein Audio gefunden")

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(
            audio_url,
            executable="ffmpeg",
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
