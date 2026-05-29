import discord
from discord.ext import commands
import wavelink
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    # 🔥 NEUE Wavelink Version
    node = wavelink.Node(
        uri="http://DEINE-RAILWAY-URL:2333",
        password="123456"
    )

    await wavelink.Pool.connect(nodes=[node], client=bot)

# ---------------- PLAY ----------------
@bot.command()
async def play(ctx, *, query: str):

    if not ctx.author.voice:
        return await ctx.send("❌ Geh in Voice!")

    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    # 🔥 SEARCH FIX
    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await ctx.send("❌ Kein Song gefunden")

    track = tracks[0]

    await vc.play(track)

    await ctx.send(f"🎶 spielt: {track.title}")

# ---------------- STOP ----------------
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ gestoppt")

bot.run(os.getenv("DISCORD_TOKEN"))
