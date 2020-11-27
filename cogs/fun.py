import discord
import config_loader
from discord.ext import commands

config = ConfigLoader()

class Fun(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == config.data["ID"]["RAGE"] and not message.content.isupper():
            await message.delete()

        elif message.channel.id == config.data["ID"]["PLEASE_IM_LOST"]:
            pass
