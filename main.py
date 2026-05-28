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


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Fehler: `{error}`")
    print("ERROR:", error)


@bot.command()
async def play(ctx, url: str):

    print("PLAY COMMAND ANGEKOMMEN")

    if not ctx.author.voice:
        return await ctx.send("❌ Du musst in einem Voice Channel sein!")

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    try:
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await ctx.send("🎶 Jetzt spielt Musik!")

    except Exception as e:
        await ctx.send(f"❌ Play Fehler: {e}")
        print("PLAY ERROR:", e)


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Gestoppt")


bot.run(os.getenv("DISCORD_TOKEN"))
