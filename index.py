import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

current_votes = {}
required_votes = 2  # kann geändert werden

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

        await interaction.response.send_message(f"👍 Vote gezählt! ({votes}/{required_votes})", ephemeral=True)

        if votes >= required_votes:
            await self.start_music(interaction)

    async def start_music(self, interaction):
        vc = self.ctx.voice_client

        if not vc:
            channel = self.ctx.author.voice.channel
            vc = await channel.connect()

        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            audio_url = info['url']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)

        vc.stop()
        vc.play(source)

        await interaction.channel.send("🎶 Musik gestartet!")

        self.stop()


@bot.command()
async def play(ctx, url: str):

    if not ctx.author.voice:
        return await ctx.send("❌ Du bist in keinem Voice Channel!")

    view = MusicView(url, ctx)

    await ctx.send("🎵 Song bereit! Drücke ▶️ um zu starten (2 Votes nötig)", view=view)


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Gestoppt")

bot.run("DEIN_BOT_TOKEN")
