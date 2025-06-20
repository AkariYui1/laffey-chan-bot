import os
import discord
from discord.ext import commands

# Bot setup with slash commands enabled
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

MessageOwner = discord.User | discord.Member
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
QUARANTINE_FILE = os.path.join(DATA_DIR, "quarantine_channels.json")
WARNINGS_FILE = os.path.join(DATA_DIR, "warnings.json")
COUNTING_FILE = os.path.join(DATA_DIR, "counting_channels.json")
VIEDICT_DIR = os.path.join(DATA_DIR, "..", "dictionary", "dictionary")
VIEDICT_FILE = os.path.join(DATA_DIR, "viedict.json")