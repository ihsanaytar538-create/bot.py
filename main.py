import discord
from discord.ext import commands
import wavelink
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot online")

    await wavelink.NodePool.create_node(
        bot=bot,
        uri="http://DEINE-RAILWAY-URL:2333",
        password="123456"
    )

@bot.command()
async def play(ctx, *, query: str):

    if not ctx.author.voice:
        return await ctx.send("Geh in Voice!")

    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    tracks = await wavelink.YouTubeTrack.search(query)
    track = tracks[0]

    await vc.play(track)

    await ctx.send("🎶 spielt: " + track.title)

bot.run(os.getenv("DISCORD_TOKEN"))
