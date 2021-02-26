#!/usr/bin/env python3

import json

from discord.ext import commands

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun

__version__ = "under developpement"

# Configuration
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

bot = commands.Bot(command_prefix=config["PREFIX"])

# Cogs load
for cog in (Omega, Moderation, Fun):
    bot.add_cog(cog(bot, config))


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} connected on {len(bot.guilds)} servers")


bot.run(config["TOKEN"])
