"""Contains cog related to moderation."""

import re
import unicodedata

import discord
from discord.ext import commands

from src.utils import user_only


class Moderation(commands.Cog):
    """Contains commands related to moderation."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        self.regex_patterns = {chan_id: re.compile(pattern)
                               for chan_id, pattern in config["REGEX_CHANNELS"].items()}

    @commands.Cog.listener()
    @user_only()
    async def on_message(self, message):
        """Delete message that does not match the channel regex."""
        pattern = self.regex_patterns.get(str(message.channel.id))
        if pattern:
            if not pattern.fullmatch(message.content):
                await message.delete()
