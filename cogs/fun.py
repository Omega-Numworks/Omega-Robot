import aiohttp

import requests
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

        # Make a request to the nekos.life api at the command's name endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://nekos.life/api/v2/img/{ctx.invoked_with}") as r:
                if r.status == 200:
                    data = await r.json()
                else:
                    # If the request status is not 200, send an error embed
                    embed.title = "API error"
                    embed.description = "Sorry, a problem has occurred when trying to interact with the nekos.life API"
                    return await ctx.send(embed)

        # Place the nekos.life's gif in the embed
        embed.set_image(url=data["url"])

        # Make a custom message based on the command's template message
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
        apod = requests.get("https://apod.nasa.gov/apod/astropix.html").text
        apod = BeautilfulSoup(apod, features="html5lib")

        img = f"https://apod.nasa.gov/apod/{apod.find_all("img")[0]["src"]}"
        text = apod.find_all("p")[2].text

        embed = discord.Embed(title="Astronomy Picture of the Day", color="")
        embed.description = "Each day a different image or photograph of our fascinating universe is featured."

        embed.set_image(img)
        embed.add_field(name="Explanation", value=text[18:])

        await ctx.send(embed=embed)
