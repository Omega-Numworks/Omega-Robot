import discord
import json
import commands.all.all_commands as all_cmd
import commands.omega.omega_commands as omega_cmd
import commands.omega_wtf.omega_wtf_commands as omega_wtf_cmd

# Configuration
with open("config.json", "r") as file:
    config = json.load(file)

omega_robot = discord.client()

# Global variables
__version__ = "under developpement"

# Instances of bot's commands
ALL_COMMANDS = all_cmd.AllCommands()
OMEGA_COMMANDS = omega_cmd.OmegaCommands()
OMEGA_WTF_COMMANDS = omega_wtf_cmd.OmegaWTFCommands()


# Bot's events
@omega_robot.event()
async def on_message(message):
    if message.author.bot:
        return

    if message.guild.id in (ID_OMEGA, ID_OMEGA_WTF):  # Both servers commands
        if message.guid.id == ID_COMEGA:  # Omega commands
            pass

        elif message.guild.id == ID_OMEGA_WTF:  # Omega WTF commands
            pass
