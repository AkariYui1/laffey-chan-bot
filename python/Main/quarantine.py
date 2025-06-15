import json
from typing import Any
from consts import QUARANTINE_FILE

def load_quarantine_channels() -> dict[str, Any]:
    """Load quarantine channels data from JSON file"""
    try:
        with open(QUARANTINE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_quarantine_channels(quarantine_data):
    """Save quarantine channels data to JSON file"""
    json.dump(quarantine_data, open(QUARANTINE_FILE, "w"), indent=2)


def increment_ban_counter(guild_id):
    """Increment the auto-ban counter for a guild"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str not in quarantine_data:
        quarantine_data[guild_str] = {
            "channels": [],
            "log_channel": None,
            "ban_count": 0,
        }
    elif isinstance(quarantine_data[guild_str], list):
        # Convert old format to new format
        quarantine_data[guild_str] = {
            "channels": quarantine_data[guild_str],
            "log_channel": None,
            "ban_count": 0,
        }
    elif "ban_count" not in quarantine_data[guild_str]:
        # Add ban_count to existing dict format
        quarantine_data[guild_str]["ban_count"] = 0

    quarantine_data[guild_str]["ban_count"] += 1
    save_quarantine_channels(quarantine_data)
    return quarantine_data[guild_str]["ban_count"]


def get_ban_count(guild_id):
    """Get the current auto-ban count for a guild"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str in quarantine_data and isinstance(quarantine_data[guild_str], dict):
        return quarantine_data[guild_str].get("ban_count", 0)
    return 0


def set_log_channel(guild_id, channel_id):
    """Set the log channel for a guild"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str not in quarantine_data:
        quarantine_data[guild_str] = {"channels": [], "log_channel": None}
    elif isinstance(quarantine_data[guild_str], list):
        # Convert old format to new format
        quarantine_data[guild_str] = {
            "channels": quarantine_data[guild_str],
            "log_channel": None,
        }

    quarantine_data[guild_str]["log_channel"] = channel_id
    save_quarantine_channels(quarantine_data)


def get_log_channel(guild_id):
    """Get the log channel for a guild"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str in quarantine_data:
        if isinstance(quarantine_data[guild_str], dict):
            return quarantine_data[guild_str].get("log_channel")
        else:
            # Old format, no log channel set
            return None
    return None


def add_quarantine_channel(guild_id, channel_id):
    """Add a channel as quarantine channel for a guild"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str not in quarantine_data:
        quarantine_data[guild_str] = {"channels": [], "log_channel": None}
    elif isinstance(quarantine_data[guild_str], list):
        # Convert old format to new format
        quarantine_data[guild_str] = {
            "channels": quarantine_data[guild_str],
            "log_channel": None,
        }

    if channel_id not in quarantine_data[guild_str]["channels"]:
        quarantine_data[guild_str]["channels"].append(channel_id)
        save_quarantine_channels(quarantine_data)
        return True
    return False


def is_quarantine_channel(guild_id, channel_id):
    """Check if a channel is a quarantine channel"""
    quarantine_data = load_quarantine_channels()
    guild_str = str(guild_id)

    if guild_str in quarantine_data:
        if isinstance(quarantine_data[guild_str], dict):
            return channel_id in quarantine_data[guild_str]["channels"]
        else:
            # Old format
            return channel_id in quarantine_data[guild_str]
    return False
