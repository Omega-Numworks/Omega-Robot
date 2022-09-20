"""Main file, intended to be launched."""

__version__ = "under developpement"

import json

from discord.ext import commands
from discord import Intents

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun, Confession
from logs.logger import logger


# Configuration.
with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Bot(commands.Bot):
    """Encapsulate a discord bot."""

    extensions = (Fun, Moderation, Omega)

    optionals = {Confession: config["CONFESSION"]["ENABLED"]}

    def __init__(self):
        super().__init__(config["PREFIX"], intents=Intents.all())

        self.description = "A bot for two Omega Discord servers."
        self.token = config["TOKEN"]

    async def on_ready(self):
        """Log information about bot launching."""
        logger.info("Bot %s connected on %s servers", self.user.name, len(self.guilds))
        await self.load_extensions()

    async def on_command(self, msg):
        """Log each command submitted. Log message provides information
        about name, author and arguments of the command.
        """
        args = msg.args[2:]

        args_info = ", ".join(repr(arg) for arg in args) if args else ""

        log_msg = (
            f"{msg.command.name} called by {msg.author} with " f"args {args_info}."
        )
        logger.info(log_msg)

    def run(self, **kwargs):
        """Start the bot and load one by one available cogs."""
        super().run(self.token)

    async def load_extensions(self):
        for cog in self.extensions:
            await self.add_cog(cog(self, config))

        for cog, requirement in self.optionals.items():
            if requirement:
                await self.add_cog(cog(self, config))


if __name__ == "__main__":
    omega_robot = Bot()
    omega_robot.run()
