import discord
from discord.ext import commands


class Fun(commands.Cog):
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.config["ID"]["RAGE"] and not message.content.isupper():
            await message.delete()

        elif message.channel.id == self.config["ID"]["PLEASE_IM_LOST"]:
            pass
