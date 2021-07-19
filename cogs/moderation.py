import re

import discord
from discord.ext import commands

from src.utils import user_only


class Moderation(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        # Compile all patterns into a dictionary as form
        # {channel_id: compiled_regex_pattern}
        self.regex_patterns = {chan_id: re.compile(pattern)
                               for chan_id, pattern in config["REGEX_CHANNELS"].items()}

    @commands.Cog.listener()
    @user_only()
    async def on_message(self, message):
        # check if the message's channel is limited with a specific message format
        pattern = self.regex_patterns.get(str(message.channel.id))
        if pattern:
            # if the message doesn't match with the format, the bot deletes it
            if not pattern.fullmatch(message.content):
                await message.delete()

    @commands.command(name="normalize")
    @user_only()
    async def normalize(self, ctx, member: discord.Member):
        """Normalize nickname of given member and rename it (ignores all non-ascii characters)."""
        normalized_nickname = member.nick.encode("ascii", errors="ignore")

        await member.edit(nick=normalized_nickname)

        embed = discord.Embed(name="Normalization")
        embed.description = (f"Nickname of {member.mention} has been "
                             f"changed to `{normalized_nickname}.")
        embed.colour = int(self.config["EMBED_COLOR"], 16)

        await ctx.send(embed=embed)
