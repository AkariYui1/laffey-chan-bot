from bot_setup import bot
import discord
from datetime import datetime
from Fun.vie_dict.logic import handle_viedict_message
from quarantine import is_quarantine_channel, increment_ban_counter, get_log_channel
from Fun.number_count.counting_logic import handle_counting_message

# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Không đủ thẩm quyền để chạy lệnh này!", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ Đã có lỗi xảy ra: {error}.", ephemeral=True
        )
        print(f"Command error: {error}")


@bot.event
async def on_message(message: discord.Message):
    # Ignore bot messages
    if message.author.bot:
        return

    await handle_counting_message(message)
    await handle_viedict_message(message)

    # Check if message is in a quarantine channel
    if message.guild and is_quarantine_channel(message.guild.id, message.channel.id):
        # Check if user is a moderator (has kick_members permission)
        if not message.author.guild_permissions.kick_members:
            try:
                # Delete the message first
                await message.delete()

                # Clear all messages in the channel from this user
                # Why?
                # async for msg in message.channel.history(limit=100):
                #     if msg.author == message.author and not msg.author.bot:
                #         try:
                #             await msg.delete()
                #         except:
                #             pass

                # Ban the user
                await message.author.ban(reason="Posted in quarantine channel")

                ban_count = increment_ban_counter(message.guild.id)

                embed = discord.Embed(
                    title="🚫 Auto ban!",
                    description=f"{message.author.mention} vừa bị ban vì đã đăng trong kênh cách ly",
                    color=discord.Color.red(),
                    timestamp=datetime.now(),
                )

                # Basic user information
                embed.add_field(
                    name="👤 User",
                    value=f"{message.author.display_name} (ID: {message.author.id})",
                    inline=True,
                )

                # Channel and message information
                embed.add_field(
                    name="📍 Kênh", value=message.channel.mention, inline=True
                )
                embed.add_field(
                    name="🏠 Guild",
                    value=f"{message.guild.name} (`{message.guild.id}`)",
                    inline=True,
                )
                embed.add_field(
                    name="🕒 Thời gian nhắn",
                    value=f"<t:{int(message.created_at.timestamp())}:F>",
                    inline=True,
                )

                # Message content (with length limit)
                message_content = \
                    message.content if message.content else "*Content không phải text*"
                
                if len(message_content) > 1000:
                    message_content = message_content[:1000] + "..."

                embed.add_field(
                    name="💬 Nội dung tin nhắn",
                    value=f"```{message_content}```",
                    inline=False,
                )

                embed.add_field(
                    name="ID tin nhắn", value=message.id, inline=False
                )

                # User avatar
                if message.author.avatar:
                    embed.set_thumbnail(url=message.author.avatar.url)

                # Footer with additional context
                embed.set_footer(text=f"Tổng số auto-ban: {ban_count}")

                # Send to log channel if set, otherwise do not log
                if (log_channel_id := get_log_channel(message.guild.id)) and \
                   (log_channel := message.guild.get_channel(log_channel_id)):
                    await log_channel.send(embed=embed)

            except discord.Forbidden:
                # If bot can't ban, send error message
                embed = discord.Embed(
                    title="⚠️ Cảnh báo",
                    description=f"Có tin nhắn từ {message.author.mention} trong kênh cấm chat nhưng bot không ban được!",
                    color=discord.Color.orange(),
                )
                await message.channel.send(embed=embed)
            except Exception as e:
                print(f"Error in quarantine channel handler: {e}")

    # Process commands
    await bot.process_commands(message)
