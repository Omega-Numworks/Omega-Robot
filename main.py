
__version__ = "under developpement"

import json

from discord.ext import commands

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun
from logs.logger import logger


# Configuration.
with open("config.json", encoding="utf-8") as file:
    config = json.load(file)


class Bot(commands.Bot):
    extensions = (
        Fun,
        Moderation,
        Omega
    )

    def __init__(self):
        super().__init__(config["PREFIX"])

        self.description = "A bot for two Omega Discord servers."
        self.token = config["TOKEN"]

    async def on_ready(self):
        print(f"Bot {self.user.name} connected on {len(self.guilds)} servers")

    async def on_command(self, msg):
        """Log each command submitted. Log message provides information
        about name, author and arguments of the command.
        """
        args = msg.args[2:]

        if args:
            args_info = f" with args {', '.join(repr(arg) for arg in args)}"
        else:
            args_info = ""

        log_msg = f"{msg.command.name} called by {msg.author}{args_info}."
        logger.info(log_msg)

    async def on_message_delete(self, msg):
        """Log each message deleted. Log message provides information
        about author, content and date of the message.
        """
        log_msg = (f"{msg.author} has deleted his message: "
                   f"{msg.content!r} sent at {msg.created_at}")
        logger.info(log_msg)

    def run(self):
        """Start the bot and load one by one available cogs."""
        for cog in self.extensions:
            self.add_cog(cog(self, config))

        super().run(self.token)


if __name__ == "__main__":
    omega_robot = Bot()
    omega_robot.run()
