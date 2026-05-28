import discord
import os
import re
import requests
import traceback
import time
import base64

# =========================
# TOKENS
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# =========================
# SPOTIFY TOKEN CACHE
# =========================
spotify_token = None
spotify_token_time = 0

def get_spotify_token():
    global spotify_token, spotify_token_time

    # Token 1 Stunde cachen
    if spotify_token and time.time() - spotify_token_time < 3500:
        return spotify_token

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("❌ Spotify Keys fehlen!")
        return None

    url = "https://accounts.spotify.com/api/token"

    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)

    try:
        result = response.json()
    except:
        print("❌ Token JSON Fehler:", response.text)
        return None

    if response.status_code != 200:
        print("❌ Spotify Token Error:", result)
        return None

    spotify_token = result.get("access_token")
    spotify_token_time = time.time()

    return spotify_token


# =========================
# TRACK INFO
# =========================
def get_track_info(track_id):
    token = get_spotify_token()

    if not token:
        return None

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    try:
        data = response.json()
    except:
        print("❌ Track JSON Fehler:", response.text)
        return None

    if response.status_code != 200:
        print("❌ Spotify Track Error:", data)
        return None

    song_name = data["name"]
    artist = data["artists"][0]["name"]
    cover = data["album"]["images"][0]["url"]

    return song_name, artist, cover


# =========================
# DISCORD BOT
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Bot online als {client.user}")


@client.event
async def on_message(message):

    if message.author.bot:
        return

    match = re.search(r"spotify\.com/.*/track/([a-zA-Z0-9]+)", message.content)

    if not match:
        return

    track_id = match.group(1)

    try:
        result = get_track_info(track_id)

        if not result:
            await message.reply("❌ Spotify API Fehler (siehe Console)")
            return

        song_name, artist, cover = result

        embed = discord.Embed(
            title="🎵 Spotify Song erkannt",
            description=f"**{song_name}**\nvon {artist}",
            color=0x1DB954
        )

        embed.set_thumbnail(url=cover)
        embed.add_field(name="Link", value=message.content, inline=False)

        await message.channel.send(embed=embed)

    except Exception:
        print(traceback.format_exc())
        await message.reply("❌ Unbekannter Fehler")


client.run(DISCORD_TOKEN)
