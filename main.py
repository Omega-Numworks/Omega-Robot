# --------------------------------------------------
# Imports
# --------------------------------------------------

import discord
import commands.all.all_commands as all_cmd
import commands.omega.omega_commands as omega_cmd
import commands.omega_wtf.omega_wtf_commands as omega_wtf_cmd

omega_robot = discord.client()

# --------------------------------------------------
# Global variables
# --------------------------------------------------

__version__ = "under developpement"
PREFIX = "&"
# TOKEN =

# --------------------------------------------------
# Instances of bot's commands
# --------------------------------------------------

ALL_COMMANDS = all_cmd.AllCommands()
OMEGA_COMMANDS = omega_cmd.OmegaCommands()
OMEGA_WTF_COMMANDS = omega_wtf_cmd.OmegaWTFCommands()

# --------------------------------------------------
# Bot's events
# --------------------------------------------------

@omega_robot.event()
async def on_message(message):
	if message.author == omega_robot.user()
		return None

	# Omega commands
	if message.guid.id == "663420259851567114": 
		pass
		
	# Commega WTF commands
	elif message.guild.id == "685936220395929600":
		pass

	# Both servers commands
	else: 
		pass
