import aiohttp

from bs4 import BeautilfulSoup

import discord
from discord.ext import commands


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
            async with session.get(f"https://nekos.life/api/v2/img/{ctx.invoked_with}") as r:
                if r.status == 200:
                    data = await r.json()
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
    async def apod(self, ctx):
        """
        This command requests the APOD (image and text).
        """
        embed = discord.Embed(title="Astronomy Picture of the Day", color="")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://apod.nasa.gov/apod/astropix.html") as r:
                if r.status == 200:
                    apod = await r.text
                else:
                    # If the request status is not 200, send an error embed.
                    embed.description = "Sorry, a problem has occurred when trying to interact with the apod website"
                    return await ctx.send(embed=embed)

        # Collect informations.
        apod = BeautilfulSoup(apod, features="html5lib")
        img = f"https://apod.nasa.gov/apod/{apod.find_all("img")[0]["src"]}"
        text = apod.find_all("p")[2].text

        # Make the embed.
        embed.description = "Each day a different image or photograph of our fascinating universe is featured."
        embed.set_image(img)
        embed.add_field(name="Explanation", value=text[18:])

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Turn off "confirm mode"
        self.confession_is_confirm_e = False

        # Ignore bots
        if message.author.bot:
            return

        # Check if Confession is enabled
        if not self.config["CONFESSION"]["ENABLED"]:
            await message.channel.send("Confession not enabled")
            return

        # Store msg if msg was sent in DM and turn on "confirm mode"
        if not message.guild:
            self.confession_is_confirm_e = True
            self.confession_msg = message
            await message.channel.send("React to this message to send it to the confession channel")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        reaction_user = await self.bot.fetch_user(reaction.user_id)
        reaction_channel = await self.bot.fetch_channel(reaction.channel_id)
        confession_channel = await self.bot.fetch_channel(self.config["CONFESSION"]["CHANNEL"])
        user_in_chan_guild = await confession_channel.guild.fetch_member(reaction.user_id)

        try:
            last_confession_msg = await confession_channel.fetch_message(confession_channel.last_message_id)
            new_count = int(last_confession_msg.content.split(":")[0]) + 1
        except discord.errors.NotFound:
            new_count = 1

        # Ignore bots
        if reaction_user.bot:
            return

        # Check if "confirm mode" is enabled
        if self.confession_is_confirm_e:
            return

        # Check if user id is the same as author id
        if self.confession_msg.author.id != reaction_user.id:
            return

        # If reaction is in DM and user is present in confession channel, send msg
        if reaction_channel.type.name == "private" and user_in_chan_guild is not None:
            self.confession_is_confirm_e = False
            await confession_channel.send(f"{new_count}: {self.confession_msg.content}")
