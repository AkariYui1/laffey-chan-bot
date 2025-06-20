import discord
import os
from dotenv import load_dotenv
from consts import DATA_DIR, bot

load_dotenv(os.path.join(DATA_DIR, "..", ".env"))
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    try:
        # For instant sync to specific guild (replace YOUR_GUILD_ID)
        # guild = discord.Object(id=YOUR_GUILD_ID)
        # synced = await bot.tree.sync(guild=guild)

        # For global sync (up to 1 hour delay)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        
        for command in synced:
            print(command.name)

    except Exception as e:
        print(f"Failed to sync commands: {e}")
