import asyncio
import re

import aiohttp

from bs4 import BeautifulSoup

import discord
from discord.ext import commands

from emoji import UNICODE_EMOJI

from src.utils import user_only


# Supported action commands with they template
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
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.command(name="hug", aliases=list(actions.keys())[1:])
    @user_only()
    async def action(self, ctx, member: discord.User):
        """A command that regroups all actions commands

        The command takes a mention as argument, the person on whom the action is performed.
        <prefix><action> <@mention>
        All the action commands are stored in the actions dictionary.
        """
        embed = discord.Embed()
        embed.set_footer(text="powered by nekos.life")

        # Make a request to the nekos.life api at the command's name endpoint.
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://nekos.life/api/v2/img/{ctx.invoked_with}") as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    # If the request status is not 200, send an error embed.
                    embed.title = "API error"
                    embed.description = "Sorry, a problem has occurred when trying to interact with the nekos.life API"
                    return await ctx.send(embed=embed)

        # Place the nekos.life's gif in the embed.
        embed.set_image(url=data["url"])

        # Make a custom message based on the command's template message.
        if ctx.author.id != member.id:
            embed.description = actions[ctx.invoked_with].format(author=ctx.author.name, target=member.name)
        else:
            embed.description = f"Aww, I see you are lonely, I will {ctx.invoked_with} you"

        await ctx.send(embed=embed)

    @commands.command()
    @user_only()
    async def apod(self, ctx):
        """
        This command requests the APOD (image and text).
        """
        embed = discord.Embed(title="Astronomy Picture of the Day")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://apod.nasa.gov/apod/") as response:
                if response.status == 200:
                    apod = await response.text()
                else:
                    # If the request status is not 200, send an error embed.
                    embed.description = "Sorry, a problem has occurred when trying to interact with the apod website"
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
        text = text.replace('  ', ' ')

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

        # Check if msg was sent in DM by a user
        if not isinstance(message.channel, discord.DMChannel) or message.author.bot:
            return

        # Check if one or more emojis are in the msg content
        pattern = "<a?:.+?:\\d+>|<:.+?:\\d+>|:[a-z_]+:"
        emoji_in_msg = bool(re.search(pattern, message.content))

        emoji_in_msg |= any(char in UNICODE_EMOJI["en"]
                            for char in message.content)
        if emoji_in_msg:
            return await message.channel.send("Please don't use any emojis in "
                                              "your confession")

        # Send a confirm message, store it as pending in the queue until it gets reacted
        confirm_message = await message.channel.send("React to this message to send it "
                                                     "to the confession channel")
        await confirm_message.add_reaction("✅")
        self.confession_queue[confirm_message.id] = message.content

        # After 30 secondes, the message is removed from the queue
        await asyncio.sleep(30)
        self.confession_queue.pop()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        # Ignore himself
        if reaction.user_id == self.bot.user.id:
            return

        # Check if the message is in the pending confessions
        # and store the confession message if so
        confession_msg = self.confession_queue.pop(reaction.message_id, None)
        if not confession_msg:
            return

        # Check that user is present in confession channel
        confession_channel = await self.bot.fetch_channel(self.config["CONFESSION"]["CHANNEL"])
        user_in_chan_guild = await confession_channel.guild.fetch_member(reaction.user_id)
        if user_in_chan_guild is None:
            return

        # Get confession number
        try:
            last_confession = await confession_channel.fetch_message(confession_channel.last_message_id)
            new_count = int(last_confession.content.split(":")[0]) + 1
        except discord.errors.NotFound:
            new_count = 1

        # Send the confession in the appropriate channel
        await confession_channel.send(f"{new_count}: {confession_msg}")
