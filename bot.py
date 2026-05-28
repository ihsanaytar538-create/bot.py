import discord
import os
import requests
import re

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# =========================
# DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# READY
# =========================
@client.event
async def on_ready():
    print(f"✅ online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    if message.author.bot:
        return

    text = message.content

    # =========================
    # SPOTIFY LINK CHECK
    # =========================
    spotify_regex = r"(https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]+)"

    match = re.search(spotify_regex, text)

    if match:

        spotify_link = match.group(1)

        # Beispiel Songdaten
        # (Spotify API wäre komplizierter)
        song_name = "spotify song"
        artist = "unknown artist"

        # MP3 Datei
        audio_path = "songs/song.mp3"

        # Prüfen ob Datei existiert
        if not os.path.exists(audio_path):
            await message.reply("❌ keine audio datei gefunden")
            return

        try:

            # Discord Datei
            file = discord.File(audio_path)

            # Embed
            embed = discord.Embed(
                title="🎵 spotify erkannt",
                description=f"**{song_name}**\nvon {artist}",
                color=0x1DB954
            )

            embed.add_field(
                name="spotify link",
                value=spotify_link,
                inline=False
            )

            embed.set_footer(
                text="direkt im discord chat abspielbar"
            )

            # SENDEN
            await message.channel.send(
                embed=embed,
                file=file
            )

        except Exception as e:
            print(e)
            await message.reply("❌ fehler")

# =========================
# BOT START
# =========================
client.run(DISCORD_TOKEN)
