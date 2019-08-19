import discord, random, asyncio, os, json

from config import settings
from discord.ext import commands

def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

quote_list = []
with open('config/phrases.json') as f:
    quote_list = json.load(f)


class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = quote_list

    async def update_quotes(self):
        with open('config/phrases.json', 'w') as f:
            json.dump(self.quotes, f, indent=2)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

    @commands.command()
    async def quote(self, ctx, action: str, *phrase):
        edit_perms = ctx.author.guild_permissions.manage_guild
        action = action.lower()
        phrase = " ".join(phrase) # input is stored as a list of words in the message, this combines it into a string e.g. ['Hello', 'World'] -> 'Hello World'

        if action == 'amount':
            await ctx.send("Current meme count: `{}`".format(len(self.quotes)))
            return

        elif action == 'search':
            str_with_phrase = []
            for quote in self.quotes:
                if phrase.casefold() in quote.casefold():
                    str_with_phrase.append(quote)

            if len(str_with_phrase) == 0:
                await ctx.send("Could not find a quote with the phrase: `{}`".format(phrase))
                return
            else:
                await ctx.send(random.choice(str_with_phrase))
                return

        elif action == 'remove':
            if not edit_perms:
                await ctx.send(f"{ctx.author.mention} You don't have permission to do that!")
                return

            str_with_phrase = []
            for quote in self.quotes:
                if phrase.casefold() in quote.casefold():
                    str_with_phrase.append(quote)

            if len(str_with_phrase) == 0:
                await ctx.send("Could not find a quote with the phrase: `{}`".format(phrase))
                return

            elif len(str_with_phrase) == 1:
                self.quotes.remove(str_with_phrase[0])
                await Quote.update_quotes(self)
                await ctx.send("Removed the quote: `{}`".format(str_with_phrase[0]))
                return
            else:
                await ctx.send("Found `{}` results for the phrase: `{}`, be more specific and try again".format(len(str_with_phrase), phrase))
                return

        elif action == 'add':
            if not edit_perms:
                await ctx.send(f"{ctx.author.mention} You don't have permission to do that!")
                return

            self.quotes.append(phrase)
            await Quote.update_quotes(self)
            await ctx.send("Added the quote: `{}`".format(phrase))
            return

        elif action == 'undo':
            if not edit_perms:
                await ctx.send(f"{ctx.author.mention} You don't have permission to do that!")
                return
                
            await ctx.send("Removing the most recent qoute: `{}`".format(self.quotes[-1]))
            del self.quotes[-1]
            await Quote.update_quotes(self)
            return

        else:
            await ctx.send("`{}` is not a valid argument.\n`!quote <add | undo | remove | search | amount> [phrase]`".format(action))
            return

def setup(bot):
    bot.add_cog(Quote(bot))
