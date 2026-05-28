import discord
from discord.ext import commands
import yt_dlp
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

required_votes = 2


class MusicView(discord.ui.View):
    def __init__(self, url, ctx):
        super().__init__(timeout=60)
        self.url = url
        self.ctx = ctx
        self.voters = set()

    @discord.ui.button(label="▶️ Play", style=discord.ButtonStyle.green)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = interaction.user

        if user.id in self.voters:
            await interaction.response.send_message("❌ Du hast schon gevotet!", ephemeral=True)
            return

        self.voters.add(user.id)
        votes = len(self.voters)

        await interaction.response.send_message(
            f"👍 Vote gezählt! ({votes}/{required_votes})",
            ephemeral=True
        )

        if votes >= required_votes:
            await self.start_music(interaction)

    async def start_music(self, interaction):

        ctx = self.ctx
        vc = ctx.voice_client

        # Wenn Bot nicht im Voice ist → joinen
        if not vc:
            if not ctx.author.voice:
                return await ctx.send("❌ Du bist in keinem Voice Channel!")

            channel = ctx.author.voice.channel
            vc = await channel.connect()

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            audio_url = info["url"]

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await interaction.channel.send("🎶 Musik läuft im Voice Channel!")

        self.stop()


@bot.command()
async def play(ctx, url: str):

    if not ctx.author.voice:
        return await ctx.send("❌ Du musst in einem Voice Channel sein!")

    view = MusicView(url, ctx)

    await ctx.send(
        "🎵 Song bereit! Drücke ▶️ um zu starten (2 Votes nötig)",
        view=view
    )


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Gestoppt")


# 🔑 TOKEN aus ENV laden
bot.run(os.getenv("DISCORD_TOKEN"))
