import discord
import os
import re
import requests

# =========================
# TOKENS AUS RAILWAY
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# =========================
# SPOTIFY TOKEN HOLEN
# =========================
def get_spotify_token():

    url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(
        url,
        data=data,
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    )

    result = response.json()

    return result["access_token"]

# =========================
# SONG INFOS HOLEN
# =========================
def get_track_info(track_id):

    token = get_spotify_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    song_name = data["name"]
    artist = data["artists"][0]["name"]
    cover = data["album"]["images"][0]["url"]

    return song_name, artist, cover

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
    print(f"✅ bot online als {client.user}")

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
    spotify_regex = r"https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)"

    match = re.search(spotify_regex, text)

    if match:

        track_id = match.group(1)

        try:

            # SONG DATEN HOLEN
            song_name, artist, cover = get_track_info(track_id)

            # AUDIO DATEI
            audio_path = "songs/song.mp3"

            # EXISTIERT DIE DATEI?
            if not os.path.exists(audio_path):
                await message.reply("❌ keine mp3 gefunden")
                return

            # DATEI SENDEN
            file = discord.File(audio_path)

            # EMBED
            embed = discord.Embed(
                title="🎵 spotify song erkannt",
                description=f"**{song_name}**\nvon {artist}",
                color=0x1DB954
            )

            embed.set_thumbnail(url=cover)

            embed.add_field(
                name="spotify link",
                value=match.group(0),
                inline=False
            )

            embed.set_footer(
                text="▶ direkt im discord chat abspielbar"
            )

            # SENDEN
            await message.channel.send(
                embed=embed,
                file=file
            )

        except Exception as e:
            print(e)
            await message.reply("❌ spotify fehler")

# =========================
# BOT START
# =========================
client.run(DISCORD_TOKEN)

mach da rein das man nur im einen discord channel rein schreiben kann also der bot soll nur im einen channel benutzen können
