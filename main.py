
__version__ = "under developpement"

import json

from discord.ext import commands

from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun


extensions = (
    Omega,
    Moderation,
    Fun
)

# Configuration.
with open("config.json", "r") as file:
    config = json.load(file)


class Bot(commands.Bot):
    
    def __init__(self):
        super().__init__(config["PREFIX"])

        self.description = "A bot for two Omega Discord servers."
        self.token = config["TOKEN"]
    
    async def on_ready(self):
        print(f"Bot {self.user.name} connected on {len(self.guilds)} servers")

    def run(self):
        # Cogs load.
        for cog in extensions:
            self.add_cog(cog(self, config))

        super().run(self.token)


if __name__ == "__main__":
    omega_robot = Bot()
    omega_robot.run()
