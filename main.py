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
    print(f"✅ Online als {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("✅ Bot funktioniert!")

@bot.command()
async def play(ctx, url: str):

    if not ctx.author.voice:
        await ctx.send("❌ Du musst in einem Voice Channel sein!")
        return

    channel = ctx.author.voice.channel

    try:
        vc = ctx.voice_client

        # Verbinden
        if vc is None:
            vc = await channel.connect()

        elif vc.channel != channel:
            await vc.move_to(channel)

        # Warten bis wirklich verbunden
        if not vc.is_connected():
            await ctx.send("❌ Voice Verbindung fehlgeschlagen")
            return

        await ctx.send("🔄 Lade Musik...")

        ydl_opts = {
            "format": "bestaudio",
            "noplaylist": True,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(
            audio_url,
            executable="/usr/bin/ffmpeg",
            **ffmpeg_options
        )

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await ctx.send(f"🎶 Spiele jetzt: {info['title']}")

    except Exception as e:
        print("PLAY ERROR:", e)
        await ctx.send(f"❌ Fehler: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Musik gestoppt")

bot.run(os.getenv("DISCORD_TOKEN"))
