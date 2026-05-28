import discord
import os
import re
import requests

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# =========================
# CHANNEL LIMIT
# =========================
ALLOWED_CHANNEL_ID = 1509380855586361454

# =========================
# DISCORD INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

    response.raise_for_status()
    result = response.json()

    return result["access_token"]

# =========================
# TRACK INFO
# =========================
def get_track_info(track_id):
    token = get_spotify_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()

    song_name = data["name"]
    artist = data["artists"][0]["name"]
    cover = data["album"]["images"][0]["url"]

    return song_name, artist, cover

# =========================
# READY
# =========================
@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

# =========================
# MESSAGE EVENT
# =========================
@client.event
async def on_message(message):

    # Debug (SEHR WICHTIG)
    print("MSG:", message.content, "CHANNEL:", message.channel.id)

    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    text = message.content

    spotify_regex = r"https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)"
    match = re.search(spotify_regex, text)

    if not match:
        return

    track_id = match.group(1)

    try:
        song_name, artist, cover = get_track_info(track_id)

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
        embed.add_field(name="Spotify Link", value=match.group(0), inline=False)
        embed.set_footer(text="▶ direkt im Discord Chat")

        await message.channel.send(embed=embed, file=file)

    except Exception as e:
        print("ERROR:", e)
        await message.reply("❌ Spotify Fehler")

# =========================
# START
# =========================
client.run(DISCORD_TOKEN)
