import os
import discord

MessageOwner = discord.User | discord.Member
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
QUARANTINE_FILE = os.path.join(DATA_DIR, "quarantine_channels.json")
WARNINGS_FILE = os.path.join(DATA_DIR, "warnings.json")
COUNTING_FILE = os.path.join(DATA_DIR, "counting_channels.json")