"""Contains cog related to fun."""

from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands

# from emoji import UNICODE_EMOJI

from src.utils import user_only


# Supported action commands with they template.
# {author} -> command author's mention
# {target} -> user pinged in the command
actions = {
    "hug": "{author} hugs {target}",
    "pat": "{author} is patting {target}",
    "kiss": "{author} kiss {target}",
    "cuddle": "{author} cuddles {target} :heart:",
    "poke": "Hey {target}! {author} poked you",
    "baka": "{target} BAKA",
    "slap": "{author} slapped {target}!"
}


class Fun(commands.Cog):
    """Contains commands related to fun."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        self.confession_is_confirm_e: Optional[bool] = None
        self.confession_msg: Optional[str] = None

    @commands.command(name="hug", aliases=list(actions.keys())[1:])
    @user_only()
    async def action(self, ctx, member: discord.User):
        """A command that regroups all actions commands

        The command takes a mention as argument, the person on whom the
        action is performed.

        <prefix><action> <@mention>
        All the action commands are stored in the actions dictionary.
        """
        embed = discord.Embed()
        embed.set_footer(text="powered by nekos.life")

        # Make a request to the nekos.life API at the command's name endpoint.
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://nekos.life/api/v2/img/{ctx.invoked_with}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    # Send an error embed.
                    embed.title = "API error"
                    embed.description = ("Sorry, a problem has occurred when "
                                         "trying to interact with the "
                                         "nekos.life API")
                    return await ctx.send(embed=embed)

        # Place the nekos.life's gif in the embed.
        embed.set_image(url=data["url"])

        # Make a custom message based on the command's template message.
        if ctx.author.id != member.id:
            embed.description = actions[ctx.invoked_with].format(author=ctx.author.name,
                                                                 target=member.name)
        else:
            embed.description = ("Aww, I see you are lonely, I will "
                                 f"{ctx.invoked_with} you")

        await ctx.send(embed=embed)

    @commands.command()
    @user_only()
    async def apod(self, ctx):
        """This command requests the APOD (image and text)."""
        embed = discord.Embed(title="Astronomy Picture of the Day")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://apod.nasa.gov/apod/") as response:
                if response.status == 200:
                    apod = await response.text()
                else:
                    # Send an error embed.
                    embed.description = ("Sorry, a problem has occurred when "
                                         "trying to interact with the apod "
                                         "website")
                    return await ctx.send(embed=embed)

        # Collect informations.
        soup = BeautifulSoup(apod, "html.parser")
        img_url = f"https://apod.nasa.gov/apod/{soup.find('img')['src']}"

        # Get the description and sanitizes it.
        text = ""
        for node in soup.find_all("p")[2]:
            if node.name == "p":
                break
            text += node.string.replace("\n", " ")
        text = text.replace("  ", " ")

        # Make the embed.
        embed.description = f"**{soup.find('b').string}**\n{text[13:]}"
        embed.set_image(url=img_url)

        await ctx.send(embed=embed)


class Confession(commands.Cog):
    """Cog dedicated to the confession feature."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        self.confession_queue = {}

    @commands.Cog.listener()
    @user_only()
    async def on_message(self, message):
        """"Decide to store message and send a confirm message."""
        self.confession_is_confirm_e = False

        # Check if Confession is enabled.
        if not self.config["CONFESSION"]["ENABLED"]:
            await message.channel.send("Confession not enabled")
            return

        # Store msg if msg was sent in DM and turn on "confirm mode".
        if not message.guild:
            self.confession_is_confirm_e = True
            self.confession_msg = message
            await message.channel.send("React to this message to send it to "
                                       "the confession channel")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """Decide to send stored confession message."""
        reaction_user = await self.bot.fetch_user(reaction.user_id)
        reaction_channel = await self.bot.fetch_channel(reaction.channel_id)
        confession_channel = await self.bot.fetch_channel(self.config["CONFESSION"]["CHANNEL"])
        user_in_chan_guild = await confession_channel.guild.fetch_member(reaction.user_id)

        if (reaction_user.bot
                or not self.confession_is_confirm_e):
            return

        # If reaction is in DM and user is present in confession channel,
        # send the message.
        if (reaction_channel.type.name == "private"
                and user_in_chan_guild is not None):
            self.confession_is_confirm_e = False
            await confession_channel.send(self.confession_msg.content)
