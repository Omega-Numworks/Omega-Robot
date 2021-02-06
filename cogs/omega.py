import aiohttp
import asyncio
from datetime import datetime
import re
from typing import AsyncGenerator

import discord
from discord.ext import commands


async def get_github_issues(message: discord.Message) -> AsyncGenerator[dict, None]:
    """Asynchronous generator that returns information on each issue,
    identified with a specific format, in the message.

    If a request error occurs, it sends a message and stops.
    """
    matches = re.findall("(?=((^| )#[0-9]+e?($| )))", message.content)

    async with aiohttp.ClientSession() as session:
        for i in matches:
            issue = i[0].strip("#e ")
            repo = "numworks/epsilon" if "e" in i[0] else "omega-numworks/omega"

            async with session.get(f"https://api.github.com/repos/{repo}/issues/{issue}") as r:
                if r.status != 200:
                    await message.channel.send(f"Erreur lors de la requête ({r.status})")
                    return
                yield await r.json()


async def make_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title=data["title"], url=data["html_url"], description=data["body"])

    # Truncate the description if it's above the maximum size
    if len(embed.description) > 2048:
        embed.description = embed.description[:2043] + "[...]"

    author = data["user"]
    embed.set_author(name=author["login"], url=author["html_url"], icon_url=author["avatar_url"])

    additional_infos = []

    if data.get("locked"):
        additional_infos.append(":lock: locked")

    pull_request = data.get("pull_request")
    if pull_request:
        additional_infos.append(":arrows_clockwise: Pull request")

        async with aiohttp.ClientSession() as session:
            async with session.get(pull_request["url"] + "/commits") as r:
                commits_data = await r.json()

        # Format all commits data into strings
        formatted = ["[`{}`]({}) {} - {}".format(commit['sha'][:7], commit['html_url'], commit['commit']['message'],
                                                 commit['committer']['login']) for commit in commits_data]

        result = "\n".join(formatted)

        # If the result is over the field's value's max size, it truncates the result
        if len(result) > 1024:
            diff = len(result) - 1024 + 4

            while diff > 0:
                line = formatted.pop(len(formatted) // 2)
                diff -= len(line) + 1

            formatted.insert(len(formatted) // 2 + 1, "...")
            result = "\n".join(formatted)

        embed.add_field(name="Commits", value=result)

    if data["comments"]:
        additional_infos.append(f":speech_balloon: Comments : {data['comments']}")

    if data["state"] == "closed":
        closed_at = datetime.strptime(data["closed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b. %d %H:%M %Y")
        additional_infos.append(f":x: Closed by {data['closed_by']['login']} on {closed_at}")
    elif data["state"] == "open":
        additional_infos.append(":white_check_mark: Open")

    if data["labels"]:
        additional_infos.append(f":label: Labels: `{'` `'.join(i['name'] for i in data['labels'])}`")
    embed.add_field(name="Additional informations", value="\n".join(additional_infos))

    return embed


class Omega(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.issue_embeds = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots
        if message.author.bot:
            return

        # Check if the message has an issue identifier in it
        if re.search("(^| )#[0-9]+e?($| )", message.content):
            async for i in get_github_issues(message):
                # Create an embed with the data from the issue
                embed = await make_embed(i)

                # Send the embed in a message, react to it and temporally store this message's id
                issue_embed = await message.channel.send(embed=embed)
                await issue_embed.add_reaction("🗑️")
                self.issue_embeds[issue_embed.id] = 1

                # After 60 seconds, it deletes it from the storage dictionary
                await asyncio.sleep(60)
                self.issue_embeds.pop(issue_embed.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        # Ignore bots
        if self.bot.get_user(reaction.user_id).bot:
            return

        # If the reaction is "🗑️" and on a message stored in issue_embeds,
        # it deletes it and set it deleted in the storage dictionary
        if reaction.emoji.name == "🗑️" and self.issue_embeds.get(reaction.message_id):
            channel = self.bot.get_channel(reaction.channel_id)
            message = await channel.fetch_message(reaction.message_id)
            await message.delete()
            self.issue_embeds[reaction.message_id] = 0
