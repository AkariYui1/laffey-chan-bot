import sys

import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "dictionary"))

from bot_setup import token
from consts import DATA_DIR, bot
from slash_cmd import *
from error_handler import *

if __name__ == "__main__":
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)
        
    bot.run(token)
