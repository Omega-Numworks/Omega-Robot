
__version__ = "under developpement"

import json

from discord.ext import commands

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun

from logs.logger import logger


extensions = (
    Omega,
    Moderation,
    Fun
)

# Configuration.
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(config["PREFIX"])

        self.description = "A bot for two Omega Discord servers."
        self.token = config["TOKEN"]

    async def on_ready(self):
        print(f"Bot {self.user.name} connected on {len(self.guilds)} servers")

    async def on_command(self, ctx):
        args = ctx.args[2:]

        if args:
            args_text = f" with args {', '.join(str(arg) for arg in args)}"
        else:
            args_text = ""

        text = f"{ctx.command.name} called by {ctx.author}{args_text}."
        logger.info(text)

    def run(self):
        # Cogs load.
        for cog in extensions:
            self.add_cog(cog(self, config))

        super().run(self.token)


if __name__ == "__main__":
    omega_robot = Bot()
    omega_robot.run()
