from discord.ext import commands
import config_loader

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun

__version__ = "under developpement"

# Configuration
config = Config_loader()

bot = commands.Bot(command_prefix=config.data["PREFIX"])

# Cogs load
for cog in (Omega, Moderation, Fun):
    bot.add_cog(cog(bot))


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} connected on {len(bot.guilds)} servers")


bot.run(config["TOKEN"])
