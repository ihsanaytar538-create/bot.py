import discord
import os
import re
import requests
import traceback

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# =========================
# SPOTIFY TOKEN
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

    if "access_token" not in result:
        print("Spotify Token Error:", result)
        return None

    return result["access_token"]

# =========================
# TRACK INFO
# =========================
def get_track_info(track_id):
    token = get_spotify_token()

    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    response = requests.get(url, headers=headers)
    data = response.json()

    if "name" not in data:
        print("Spotify Track Error:", data)
        return None

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
    print(f"✅ Bot online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    if message.author.bot:
        return

    print("MESSAGE:", message.content)

    # ROBUSTER SPOTIFY MATCH (wichtig!)
    match = re.search(r"track/([a-zA-Z0-9]+)", message.content)

    if not match:
        return

    track_id = match.group(1)

    try:
        result = get_track_info(track_id)

        if not result:
            await message.reply("❌ Spotify API Fehler")
            return

        song_name, artist, cover = result

        audio_path = "songs/song.mp3"

        if not os.path.exists(audio_path):
            await message.reply("❌ keine mp3 gefunden")
            return

        file = discord.File(audio_path)

        embed = discord.Embed(
            title="🎵 Spotify Song erkannt",
            description=f"**{song_name}**\nvon {artist}",
            color=0x1DB954
        )

        embed.set_thumbnail(url=cover)
        embed.add_field(name="Spotify Link", value=message.content, inline=False)
        embed.set_footer(text="▶ Bot aktiv")

        await message.channel.send(embed=embed, file=file)

    except Exception:
        print(traceback.format_exc())
        await message.reply("❌ Fehler beim Verarbeiten")

# =========================
# START
# =========================
client.run(DISCORD_TOKEN)
