from datetime import datetime
import json
import random

import discord
from dictionary import Dictionary
from Main.consts import VIEDICT_DIR, VIEDICT_FILE

dictionary: Dictionary | None = None
if not dictionary or dictionary.words:
    dictionary = Dictionary()
    dictionary.load(VIEDICT_DIR)
    for i in range(len(dictionary.words)):
        dictionary.words[i].text = dictionary.words[i].text.lower()
        

def load_saved_viedict_datas() -> dict:
    try:
        return json.load(open(VIEDICT_FILE, "r"))
    except:
        return {}

def save_viedict_data(data: dict):
    json.dump(data, open(VIEDICT_FILE, "w"), indent=2)

def add_viedict_channel(guild_id, channel_id):
    loaded = load_saved_viedict_datas()
    guild_str = str(guild_id)
    
    if not guild_id in loaded:
        loaded[guild_str] = {
            "channel_id": None,
            "current_word": random.choice(dictionary.words).text,
            "last_user_id": None,
            "high_score": 0,
            "total_score": 0,
            "user_stats": {}
        }

    loaded[guild_str]["channel_id"] = channel_id
    save_viedict_data(loaded)
    return True

def get_viedict_channel(guild_id):
    loaded = load_saved_viedict_datas()
    guild_str = str(guild_id)

    if guild_str in loaded:
        return loaded[guild_str].get("channel_id")
    return None

def is_viedict_channel(guild_id, channel_id):
    return get_viedict_channel(guild_id) == channel_id

async def setup_viedict_channel(guild, moderator, response_func, category_name="Fun", ephemeral=False):
    # Check if we have the necessary permissions
    if not guild.me.guild_permissions.manage_channels:
        error_msg = "❌ Không có quyền tạo kênh!"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None

    # Create or find a category for fun channels
    category = None
    for existing_category in guild.categories:
        if existing_category.name.lower() == category_name.lower():
            category = existing_category
            break

    if not category:
        try:
            category = await guild.create_category(category_name)
        except discord.Forbidden:
            error_msg = "❌ Không có quyền tạo nhóm kênh!"
            if ephemeral:
                await response_func(error_msg, ephemeral=True)
            else:
                await response_func(error_msg)
            return None

    # Create counting channel
    viedict_channel = None
    try:
        everyone_role = guild.default_role
        counting_overwrites = {
            everyone_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                create_public_threads=False,
                create_private_threads=False,
                send_messages_in_threads=False,
                attach_files=False,
                add_reactions=False,
                use_application_commands=False,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                embed_links=True,
                attach_files=True,
                manage_messages=True,
                add_reactions=True,
            ),
        }

        viedict_channel = await guild.create_text_channel(
            name="nối-từ-tiếng-Việt",
            category=category,
            overwrites=counting_overwrites,
            topic="",
        )

        # Add channel to the database
        add_viedict_channel(guild.id, viedict_channel.id)

        # Create initial message in the counting channel
        initial_embed = discord.Embed(
            title="Nối từ tiếng Việt :clueful:",
            description="Luật khá đơn giản: lấy từ cuối cùng trong cụm từ trước và gửi vào 1 cụm từ bắt đầu bằng từ cuối ấy.",
            color=discord.Color.blue(),
        )
        initial_embed.add_field(
            name="Yêu cầu",
            value="Cụm từ mới bắt đầu bằng từ cuối của cụm từ trước (ví dụ xin chào -> chào hỏi). **Không trùng với (cụm) từ trước!**",
            inline=False,
        )
        initial_embed.add_field(
            name="Có điểm dừng không?",
            value="Có. Nếu như không thể nối tiếp được (ví dụ như chảnh chọe) hoặc sai quá 3 lần, bot sẽ đưa ra (cụm) từ mới.",
            inline=False,
        )
        await viedict_channel.send(embed=initial_embed)

        # Send success message
        embed = discord.Embed(
            title="VieDict Channel Setup Complete",
            description=f"Tạo kênh thành công: {viedict_channel.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Moderator", value=moderator.mention, inline=True)

        if ephemeral:
            await response_func(embed=embed, ephemeral=True)
        else:
            await response_func(embed=embed)

    except discord.Forbidden:
        error_msg = "❌ I don't have permission to create or configure the counting channel!"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None

    return viedict_channel

async def setup_viedict_in_existing_channel(channel, moderator, response_func, ephemeral=False):
    """Setup counting in an existing channel"""
    
    # Check if we have the necessary permissions in this channel
    if not channel.permissions_for(channel.guild.me).manage_messages:
        error_msg = "❌ I don't have permission to manage messages in that channel!"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None

    if not channel.permissions_for(channel.guild.me).add_reactions:
        error_msg = "❌ I don't have permission to add reactions in that channel!"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None

    try:
        # Add channel to the database
        add_viedict_channel(channel.guild.id, channel.id)

        # Create initial message in the counting channel
        initial_embed = discord.Embed(
            title="Nối từ tiếng Việt :clueful:",
            description="Luật khá đơn giản: lấy từ cuối cùng trong cụm từ trước và gửi vào 1 cụm từ bắt đầu bằng từ cuối ấy.",
            color=discord.Color.blue(),
        )
        initial_embed.add_field(
            name="Yêu cầu",
            value="Cụm từ mới bắt đầu bằng từ cuối của cụm từ trước (ví dụ xin chào -> chào hỏi). **Không trùng với (cụm) từ trước!**",
            inline=False,
        )
        initial_embed.add_field(
            name="Có điểm dừng không?",
            value="Có. Nếu như không thể nối tiếp được (ví dụ như chảnh chọe) hoặc sai quá 3 lần, bot sẽ đưa ra (cụm) từ mới.",
            inline=False,
        )
        await channel.send(embed=initial_embed)

        # Send success message
        embed = discord.Embed(
            title="Setup kênh Viedict thành công",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="Channel", value=channel.mention, inline=True)

        if ephemeral:
            await response_func(embed=embed, ephemeral=True)
        else:
            await response_func(embed=embed)

    except discord.Forbidden:
        error_msg = "❌ I don't have permission to send messages in that channel!"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None
    except Exception as e:
        error_msg = f"❌ Failed to setup tieing words in that channel: {str(e)}"
        if ephemeral:
            await response_func(error_msg, ephemeral=True)
        else:
            await response_func(error_msg)
        return None

    return channel