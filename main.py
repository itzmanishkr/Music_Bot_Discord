import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import yt_dlp
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global Queue
music_queue = []

# YT-DLP Options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'default_search': 'ytsearch'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


@bot.event
async def on_ready():
    print(f"🎵 Logged in as {bot.user}")


# Join
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ Joined voice channel")
    else:
        await ctx.send("❌ Join a voice channel first.")


# Leave
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left voice channel")
    else:
        await ctx.send("❌ I'm not in a voice channel.")


# Play next song from queue
async def play_next(ctx):
    if len(music_queue) > 0:
        song = music_queue.pop(0)

        source = await discord.FFmpegOpusAudio.from_probe(
            song["url"],
            **ffmpeg_options
        )

        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx), bot.loop
            )
        )

        await ctx.send(f"🎶 Now Playing: {song['title']}")
    else:
        await ctx.send("📂 Queue is empty.")


@bot.command()
async def play(ctx, *, query=None):
    vc = ctx.voice_client

    # If paused and no new song given → resume
    if vc and vc.is_paused() and query is None:
        vc.resume()
        await ctx.send("▶ Resumed.")
        return

    if not ctx.author.voice:
        await ctx.send("❌ Join a voice channel first.")
        return

    if not vc:
        await ctx.author.voice.channel.connect()
        vc = ctx.voice_client

    if not query:
        await ctx.send("❌ Provide a song name or URL.")
        return

    await ctx.send("🔎 Searching...")

    loop = asyncio.get_event_loop()

    try:
        data = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(query, download=False)
        )

        if 'entries' in data:
            data = data['entries'][0]

        song = {
            "title": data['title'],
            "url": data['url']
        }

        music_queue.append(song)

        await ctx.send(f"✅ Added to queue: {song['title']}")

        # If nothing playing → start next
        if not vc.is_playing() and not vc.is_paused():
            await play_next(ctx)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

        
#  Pause command
@bot.command()
async def pause(ctx):
    vc = ctx.voice_client

    if not vc:
        return await ctx.send("❌ I'm not in a voice channel.")

    if vc.is_playing():
        vc.pause()
        await ctx.send("⏸ Paused.")
    else:
        await ctx.send("❌ Nothing is playing.")

# Skip command
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Skipped!")
    else:
        await ctx.send("❌ Nothing is playing.")


# Stop and clear queue
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        music_queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⏹ Stopped and cleared queue.")
    else:
        await ctx.send("❌ Nothing is playing.")


bot.run(TOKEN)
