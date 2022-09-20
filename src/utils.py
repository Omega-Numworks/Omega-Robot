"""Contains unrelated bot functions used in ``cogs/`` """

from discord.ext import commands


def user_only():
    """A decorator to assume the author of message is not a bot."""

    async def predicate(ctx) -> bool:
        return not ctx.author.bot

    return commands.check(predicate)
