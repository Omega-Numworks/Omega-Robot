import discord
from discord.ext import commands

import re


class Moderation(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message):
        # check in the config if the message's channel
        # is limited with a specific message format
        pattern = self.config["REGEX_CHANNELS"].get(str(message.channel.id))
        if pattern:
            # if the message doesn't match with the format, the bot deletes it
            if not re.match(pattern, message.content):
                await message.delete()
