from bot_setup import bot, token
import os.path

from .consts import DATA_DIR

if __name__ == "__main__":
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)
        
    bot.run(token)
