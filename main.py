import discord
import os
import re
import requests
import traceback
import time
import base64

# ==========================================
# DISCORD + SPOTIFY TOKENS
# ==========================================

DISCORD_TOKEN = "DEIN_DISCORD_TOKEN"

SPOTIFY_CLIENT_ID = "DEINE_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "DEIN_SPOTIFY_CLIENT_SECRET"

# ==========================================
# SPOTIFY TOKEN CACHE
# ==========================================

spotify_token = None
spotify_token_time = 0


# ==========================================
# SPOTIFY ACCESS TOKEN HOLEN
# ==========================================

def get_spotify_token():
    global spotify_token
    global spotify_token_time

    # Token cachen
    if spotify_token and time.time() - spotify_token_time < 3000:
        return spotify_token

    url = "https://accounts.spotify.com/api/token"

    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)

    try:
        result = response.json()
    except Exception:
        print("❌ Spotify Token JSON Fehler")
        print(response.text)
        return None

    if response.status_code != 200:
        print("❌ Spotify Token Fehler:")
        print(result)
        return None

    spotify_token = result["access_token"]
    spotify_token_time = time.time()

    print("✅ Neuer Spotify Token geladen")

    return spotify_token


# ==========================================
# TRACK INFO HOLEN
# ==========================================

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
    except Exception:
        print("❌ Spotify Track JSON Fehler")
        print(response.text)
        return None

    if response.status_code != 200:
        print("❌ Spotify Track Fehler:")
        print(data)
        return None

    song_name = data["name"]
    artist = data["artists"][0]["name"]
    album = data["album"]["name"]
    cover = data["album"]["images"][0]["url"]
    spotify_url = data["external_urls"]["spotify"]

    return {
        "song_name": song_name,
        "artist": artist,
        "album": album,
        "cover": cover,
        "spotify_url": spotify_url
    }


# ==========================================
# DISCORD BOT SETUP
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# ==========================================
# BOT READY
# ==========================================

@client.event
async def on_ready():
    print("===================================")
    print(f"✅ Bot online als {client.user}")
    print("===================================")


# ==========================================
# MESSAGE EVENT
# ==========================================

@client.event
async def on_message(message):

    # Bots ignorieren
    if message.author.bot:
        return

    # Spotify Track erkennen
    match = re.search(
        r"(?:https:\/\/)?open\.spotify\.com\/(?:intl-\w+\/)?track\/([A-Za-z0-9]+)",
        message.content
    )

    if not match:
        return

    track_id = match.group(1)

    print(f"🎵 Spotify Track erkannt: {track_id}")

    try:

        result = get_track_info(track_id)

        if not result:
            await message.reply("❌ Spotify API Fehler")
            return

        # Daten
        song_name = result["song_name"]
        artist = result["artist"]
        album = result["album"]
        cover = result["cover"]
        spotify_url = result["spotify_url"]

        # Embed
        embed = discord.Embed(
            title="🎵 Spotify Song erkannt",
            description=f"**{song_name}**\n👤 {artist}",
            color=0x1DB954
        )

        embed.set_thumbnail(url=cover)

        embed.add_field(
            name="💿 Album",
            value=album,
            inline=False
        )

        embed.add_field(
            name="🔗 Spotify Link",
            value=spotify_url,
            inline=False
        )

        embed.set_footer(
            text=f"Gepostet von {message.author}",
            icon_url=message.author.display_avatar.url
        )

        await message.channel.send(embed=embed)

    except Exception:
        print("❌ Unbekannter Fehler:")
        print(traceback.format_exc())

        await message.reply("❌ Unbekannter Fehler")


# ==========================================
# BOT STARTEN
# ==========================================

client.run(DISCORD_TOKEN)
