from bot_setup import bot
import discord  # type: ignore
from warn_logic import (
    warn_user_logic,
    check_warnings_logic,
    remove_warnings_logic,
    clear_warnings_logic,
    remove_timeout_logic,
)
from channels import setup_quarantine_channel, setup_log_channel
from .consts import MessageOwner
from Fun.number_count.counting_logic import get_counting_stats
from Fun.number_count.counting_setup import setup_counting_channel, setup_counting_in_existing_channel

async def isAdmin(interaction: discord.Interaction):
    """
    Verifies if the user that invokes the bot command/whatever is a server
    moderator or not. If not, a message will be sent and this function will return False. Otherwise return True.
    """
    assert interaction or user

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            "❌ Không đủ thẩm quyền!", ephemeral=True
        )
        return False
    return True

@bot.tree.command(name="warn", description="Cảnh báo thành viên bất kì (trừ bản thân người sử dụng và bot)")
async def warn_slash(
    interaction: discord.Interaction, user: discord.Member, reason: str
):
    if not await isAdmin(interaction): return

    await warn_user_logic(
        user,
        interaction.user,
        reason,
        interaction.guild,
        interaction.response.send_message,
    )


@bot.tree.command(name="warnings", description="Xem những lần thành viên bị cảnh cáo")
async def warnings_slash(interaction: discord.Interaction, user: MessageOwner | None = None):
    # Default to command user if no user specified
    if user is None:
        user = interaction.user

    # Check permissions - users can check their own warnings, moderators can check anyone's
    if user.id != interaction.user.id and \
            not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            "❌ Không đủ thẩm quyền để xem các cảnh báo đến người dùng khác!",
            ephemeral=True,
        )
        return

    await check_warnings_logic(
        user, interaction.user, interaction.response.send_message, ephemeral=True
    )


@bot.tree.command(
    name="removewarnings",
    description="Gỡ bỏ số cảnh cáo nhất định khỏi 1 thành viên nào đó",
)
async def removewarnings_slash(
    interaction: discord.Interaction, user: discord.Member, amount: int
):
    # Check permissions (moderators can remove warnings)
    if not await isAdmin(interaction): return

    if amount <= 0:
        await interaction.response.send_message(
            "❌ Ai đời lại gỡ bỏ âm số cảnh báo?", ephemeral=True
        )
        return

    await remove_warnings_logic(
        user,
        interaction.user,
        interaction.guild,
        amount,
        interaction.response.send_message,
        ephemeral=True,
    )

@bot.tree.command(name="clearwarnings", description="Gỡ mọi cảnh báo tới 1 thành viên")
async def clearwarnings_slash(interaction: discord.Interaction, user: discord.Member):
    if not await isAdmin(interaction): return

    await clear_warnings_logic(
        user,
        interaction.user,
        interaction.guild,
        interaction.response.send_message,
        ephemeral=True,
    )


@bot.tree.command(
    name="setupquarantine",
    description="Setup kênh auto-ban những ai không phải mod mà nhắn vào kênh",
)
async def setupquarantine_slash(
    interaction: discord.Interaction, category_name: str = "Moderation"
):
    """Setup quarantine channel with slash command"""
    # Check for specific permissions instead of administrator
    if not (
        interaction.user.guild_permissions.manage_channels
        and interaction.user.guild_permissions.manage_roles
    ):
        await interaction.response.send_message(
            "❌ You need 'Manage Channels' and 'Manage Roles' permissions to set up a quarantine channel!",
            ephemeral=True,
        )
        return

    await setup_quarantine_channel(
        interaction.guild,
        interaction.user,
        interaction.response.send_message,
        category_name,
        ephemeral=True,
    )


@bot.tree.command(
    name="setuplog", description="Setup log channel for moderation actions"
)
async def setuplog_slash(
    interaction: discord.Interaction, category_name: str = "Moderation"
):
    """Setup log channel with slash command"""
    # Check for specific permissions instead of administrator
    if not (
        interaction.user.guild_permissions.manage_channels
        and interaction.user.guild_permissions.manage_roles
    ):
        await interaction.response.send_message(
            "❌ You need 'Manage Channels' and 'Manage Roles' permissions to set up a log channel!",
            ephemeral=True,
        )
        return

    await setup_log_channel(
        interaction.guild,
        interaction.user,
        interaction.response.send_message,
        category_name,
        ephemeral=True,
    )


@bot.tree.command(name="removetimeout", description="Remove timeout from a user")
async def removetimeout_slash(interaction: discord.Interaction, user: discord.Member):
    if not await isAdmin(interaction): return

    await remove_timeout_logic(
        user, interaction.user, interaction.response.send_message, ephemeral=True
    )

@bot.tree.command(name="setupcounting", description="Setup a counting channel for the server")
async def setupcounting_slash(
    interaction: discord.Interaction, 
    channel: discord.TextChannel = None,
    category_name: str = "Fun"
):
    """Setup counting channel with slash command"""
    # Check for specific permissions
    if not (
        interaction.user.guild_permissions.manage_channels
        and interaction.user.guild_permissions.manage_roles
    ):
        await interaction.response.send_message(
            "❌ Cần quyền quản lí kênh và role để tạo kênh!",
            ephemeral=True,
        )
        return

    if channel:
        # Setup counting in the specified existing channel
        await setup_counting_in_existing_channel(
            channel,
            interaction.user,
            interaction.response.send_message,
            ephemeral=True,
        )
    else:
        # Create a new counting channel
        await setup_counting_channel(
            interaction.guild,
            interaction.user,
            interaction.response.send_message,
            category_name,
            ephemeral=True,
        )


@bot.tree.command(name="countingstats", description="View counting statistics")
async def countingstats_slash(
    interaction: discord.Interaction, user: discord.Member | None = None
):
    """View counting statistics for server or specific user"""

    stats = await get_counting_stats(interaction.guild.id, user)
    if not stats:
        await interaction.response.send_message(
            "❌ No counting channel set up for this server!", ephemeral=True
        )
        return
    if user:
        embed = discord.Embed(
            title=f"🔢 Chỉ số đếm số của {user.display_name}",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="✅ Đúng", value=f"{stats['correct']}", inline=True)
        embed.add_field(name="❌ Sai", value=f"{stats['failed']}", inline=True)
        embed.add_field(name="🎯 Độ chính xác", value=f"{stats['accuracy']:.1f}%", inline=True)

    else:
        embed = discord.Embed(
            title=f"🔢 Chỉ số đếm số của toàn server",
            color=discord.Color.blue(),
        )
        embed.add_field(name="🔢 Số hiện tại", value=f"{stats['current_number']}", inline=True)
        embed.add_field(name="🏆 Điểm cao nhất", value=f"{stats['high_score']}", inline=True)
        embed.add_field(name="📊 Đếm được", value=f"{stats['total_counts']}", inline=True)

        # Show top 5 counters
        user_stats = stats["user_stats"]
        if user_stats:
            sorted_users = sorted(
                user_stats.items(), key=lambda x: x[1]["correct"], reverse=True
            )[:5]
            leaderboard = ""
            for i, (user_id, user_data) in enumerate(sorted_users, 1):
                user_obj = interaction.guild.get_member(int(user_id))
                user_name = user_obj.display_name if user_obj else "<Không xác định>"
                leaderboard += f"{i}. {user_name}: {user_data['correct']} lần đếm đúng\n"

            if leaderboard:
                embed.add_field(
                    name="🏅 Top nghiện đếm số", value=leaderboard, inline=False
                )

    await interaction.response.send_message(embed=embed, ephemeral=True)