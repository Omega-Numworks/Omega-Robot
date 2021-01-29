import re

import discord
from discord.ext import commands


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

    @commands.command(name="normalize")
    async def normalize(self, ctx, member: discord.Member):
        """Normalize nickname of given member and rename it (ignores all non-ascii characters)."""
        normalized_nickname = member.nick.encode("ascii", errors="ignore")

        await member.edit(nick=normalized_nickname)

        embed = discord.Embed(name="Normalization")
        embed.description = f"Nickname of {member.mention} has been changed to `{normalized_nickname}."
        embed.color = int(self.config["EMBED_COLOR"], 16)

        await ctx.send(embed=embed)