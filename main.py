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
async def play(ctx, url: str):

    # User muss im Voice sein
    if not ctx.author.voice:
        await ctx.send("❌ Du musst in einem Voice Channel sein!")
        return

    channel = ctx.author.voice.channel

    vc = ctx.voice_client

    try:
        # Bot verbinden
        if vc is None:
            vc = await channel.connect()

        # Nur moven wenn anderer Channel
        elif vc.channel != channel:
            await vc.move_to(channel)

        await ctx.send("🔄 Lade Musik...")

        # YouTube laden
        ydl_opts = {
            "format": "bestaudio",
            "noplaylist": True,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(
            stream_url,
            executable="ffmpeg",
            **ffmpeg_options
        )

        # Alte Musik stoppen
        if vc.is_playing():
            vc.stop()

        # Musik starten
        vc.play(source)

        await ctx.send(f"🎶 Spiele jetzt: {info['title']}")

    except Exception as e:
        print("PLAY ERROR:", e)
        await ctx.send(f"❌ Fehler: {e}")

# ---------------- STOP ----------------
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Musik gestoppt")

# ---------------- ERROR ----------------
@bot.event
async def on_command_error(ctx, error):
    print("ERROR:", error)
    await ctx.send(f"❌ Fehler: {error}")

# ---------------- START ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
