import discord
from Fun.vie_dict.setup import *

def extract_first_word(text: str): return text.strip().split(" ")[0].lower()
def extract_last_word(text: str): return text.strip().split(" ")[-1].lower()

async def handle_viedict_message(msg: discord.Message):
    if not msg.guild or msg.author.bot: return
    if not is_viedict_channel(msg.guild.id, msg.channel.id): return

    loaded = load_saved_viedict_datas()
    guild_str = str(msg.guild.id)

    if guild_str not in loaded: return

    guild_data = loaded[guild_str]
    last_user_id = guild_data.get("last_user_id")
    current_word = guild_data.get("current_word")
    total_score = guild_data.get("total_score", 0)
    high_score = guild_data.get("high_score", 0)

    user_id_str = str(msg.author.id)
    user_stats = guild_data.get("user_stats", {})
    if user_id_str not in user_stats:
        user_stats[user_id_str] = {"correct": 0, "failed": 0}

    if msg.content.strip().lower() == "resetvi":
        guild_data["last_user_id"] = None
        guild_data["current_word"] = random.choice(dictionary.words).text
        save_viedict_data(loaded)

        embed = discord.Embed(title="Đã reset nối từ tiếng Việt", description=f"Bắt đầu với {guild_data['current_word']}", color=discord.Color.orange())
        embed.add_field(name="Tổng số từ nối", value=total_score, inline=True)
        embed.add_field(name="Điểm cao nhất", value=high_score, inline=True)

        await msg.channel.send(embed=embed)
        return
    
    if last_user_id == msg.author.id:
        await msg.delete()
        warning_msg = await msg.channel.send(f"❌ Vui lòng chờ người khác nối từ trước")
        # Auto-delete the warning message after 5 seconds
        await warning_msg.delete(delay=5)
        return

    input_word = extract_first_word(msg.content)
    if not input_word:
        await msg.delete()
        warning_msg = await msg.channel.send(f"❌ Không phát hiện được từ nào hợp lệ để kiểm tra")
        # Auto-delete the warning message after 5 seconds
        await warning_msg.delete(delay=5)
        return
    
    last_word = extract_last_word(current_word)
    guild_data["last_user_id"] = msg.author.id
    
    if input_word != last_word:
        # await msg.delete()
        await msg.add_reaction("<:no:761520109864747030>")
        warning_msg = await msg.channel.send(f"❌ Từ đầu tiên không trùng với từ cuối của (cụm) từ trước: {current_word}")
        # Auto-delete the warning message after 5 seconds
        await warning_msg.delete(delay=5)
        user_stats[user_id_str]["failed"] += 1
        return
    else:
        foundWord: bool = False

        for word in dictionary.words:
            if msg.content.lower() == word.text:
                foundWord = True
                await msg.add_reaction("<a:tick:1382402150365397022>")

                guild_data["current_word"] = msg.content
                guild_data["total_score"] += 1
                guild_data["high_score"] += 1
                user_stats[user_id_str]["correct"] += 1
                break
        
        if not foundWord:
            await msg.add_reaction("<:no:761520109864747030>")
            user_stats[user_id_str]["failed"] += 1
            warning_msg = await msg.channel.send(f"❌ Không thấy (cụm) từ này trong từ điển!")
            # Auto-delete the warning message after 5 seconds
            await warning_msg.delete(delay=5)

    guild_data["user_stats"] = user_stats
    loaded[guild_str] = guild_data

    save_viedict_data(loaded)

async def get_tieing_stats(guild_id, user: discord.User | None = None):
    loaded = load_saved_viedict_datas()
    guild_str = str(guild_id)
    
    if guild_str not in loaded: return

    guild_data = loaded[guild_str]

    if user:
        user_stats = guild_data["user_stats"].get(str(user.id), {"correct": 0, "failed": 0})
        return {
            "user": user,
            "correct": user_stats["correct"],
            "failed": user_stats["failed"],
            "accuracy": user_stats["correct"] / (user_stats["correct"] + user_stats["failed"]) * 100 if (user_stats["correct"] + user_stats["failed"]) > 0 else 0
        }
    
    return {
        "current_word": guild_data.get("current_number", 0),
        "high_score": guild_data.get("high_score", 0),
        "total_score": guild_data.get("total_counts", 0),
        "user_stats": guild_data.get("user_stats", {})
    }