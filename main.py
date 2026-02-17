# import discord
# from discord.ext import commands
# import logging
# from  dotenv import load_dotenv
# import os

# load_dotenv()

# token = os.getenv('DISCORD_TOKEN')

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# # logging.basicConfig(level=logging.INFO, handlers=[handler])
# intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True

# bot = commands.Bot(command_prefix='!', intents=intents)
# secret_role = "GamersTest"

# @bot.event
# async def on_ready():
#     print(f'{bot.user.name} has connected to Discord!')

# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server, {member.name}!")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     # if message.content.startswith('!hello'):
#     #     await message.channel.send(f'Hello, {message.author.mention}!')

#     if "shit" in message.content.lower():
#         await message.delete()
#         await message.channel.send(f"{message.author.mention}, Please watch your language!")

#     await bot.process_commands(message)

# @bot.command()
# async def hello(ctx):
#     await ctx.send(f'Hello, {ctx.author.mention}!')

# @bot.command()
# async def assist(ctx):
#     await ctx.send(f'How can I assist you, {ctx.author.mention}?')

# @bot.command()
# async def helps(ctx):
#     help_message = (
#         "Here are the commands you can use:\n"
#         "!hello - Greet the bot\n"
#         "!assist - Ask for assistance\n"
#         "!help - Show this help message"
#     )
#     await ctx.send(help_message)

# # @bot.command()
# # async def assign_role(ctx, role: discord.Role, member: discord.Member):
# #     await member.add_roles(role)
# #     await ctx.send(f"{member.mention} has been assigned the {role.name} role.")

# @bot.command()
# async def assign(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=secret_role)
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"{ctx.author.mention} has been assigned the {role.name} role.")
#     else:
#         await ctx.send(f"Role '{secret_role}' not found.")
        
# @bot.command()
# async def remove(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=secret_role)
#     if role:
#         await ctx.author.remove_roles(role)
#         await ctx.send(f"{ctx.author.mention} has been removed from the {role.name} role.")
#     else:
#         await ctx.send(f"Role '{secret_role}' not found.")
    
    
# # @bot.command()
# # async def dm(ctx, *, msg):
# #     await ctx.author.send(f"You said {msg}")

# @bot.command()
# async def reply(ctx):
#     await ctx.reply("This is a reply to your message!")

# @bot.command()
# async def poll(ctx, *, question):
#     embed = discord.Embed(title="New Poll", description=question)
#     poll_message = await ctx.send(embed=embed)
#     await poll_message.add_reaction("👍")
#     await poll_message.add_reaction("👎")

# @bot.command()
# @commands.has_role(secret_role)
# async def secret(ctx):
#     await ctx.send("Welcome to the club!")

# @secret.error
# async def secret_error(ctx, error):
#     if isinstance(error, commands.MissingRole):
#         await ctx.send("You do not have permission to do that!")


# # DM command
# @bot.command()
# @commands.has_permissions(administrator=True)
# async def dm(ctx, member: discord.Member, *, message):
#     try:
#         await member.send(message)
#         await ctx.send(f"✅ Message sent to {member.mention}")
#     except discord.Forbidden:
#         await ctx.send("❌ I cannot DM this user (DMs might be disabled).")



# # Command to add role
# @bot.command()
# async def addrole(ctx, member: discord.Member, role: discord.Role):
#     await member.add_roles(role)
#     await ctx.send(f"✅ Added {role.name} to {member.mention}")

# # # Command to remove role
# # @bot.command()
# # async def removerole(ctx, member: discord.Member, role: discord.Role):
# #     await member.remove_roles(role)
# #     await ctx.send(f"❌ Removed {role.name} from {member.mention}")


# # @bot.command()
# # @commands.has_permissions(administrator=True)
# # async def addroles(ctx, member: discord.Member, role: discord.Role):
# #     await member.add_roles(role)
# #     await ctx.send("✅ Role added!")


# # @bot.command()
# # @commands.has_permissions(administrator=True)
# # async def removeroles(ctx, member: discord.Member, role: discord.Role):
# #     await member.remove_roles(role)
# #     await ctx.send("❌ Role removed!")

# bot.run(token, log_handler=handler, log_level=logging.DEBUG)




















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