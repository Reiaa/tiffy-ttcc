import discord, random, asyncio, json

from config import settings
from discord.ext import commands

def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

def get_quotes():
    with open('config/phrases.json') as f:
        return json.load(f)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def selfdestruct(message):
        await asyncio.sleep(1)
        await message.channel.send("Initiating self destruct in 5...")
        await asyncio.sleep(1)
        await message.channel.send("4...")
        await asyncio.sleep(1)
        await message.channel.send("3...")
        await asyncio.sleep(1)
        await message.channel.send("2...")
        await asyncio.sleep(1)
        await message.channel.send("1...")
        await asyncio.sleep(1)
        await message.channel.send("Goodbye :-(")
        quit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions and not(message.content.startswith('!')):
            random_phrase = random.choice(get_quotes())
            await message.channel.send(random_phrase)
            # if random_phrase == "Nock is a GOD. Wait...":
            #     await Fun.selfdestruct(message) # sorry aly :( i dont want heroku to get mad
            return

        if ('counterclaim'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            counterclaim_phrases = []
            for phrase in get_quotes():
                if 'counterclaim'.casefold() in phrase.casefold():
                    counterclaim_phrases.append(phrase)
            await message.channel.send(random.choice(counterclaim_phrases))
            return

        if ('gone'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            await message.channel.send(':crab:')
            return

        if ('hi bot'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            await message.channel.send('hi how are you')
            return

    @commands.command(aliases=['ss', 'share'])
    async def screenshare(self, ctx):
        member: discord.Member = ctx.author
        for channel in member.guild.channels:  # Loop through a list of channel objects in the guild
            if not isinstance(channel, discord.VoiceChannel):  # Current channel isn't a voice channel, check next one
                continue

            # We have a voice channel, check to see if our user is in the channel
            if member in channel.members:
                guild_id = member.guild.id  # Get the guild ID
                channel_id = channel.id  # Get the Channel ID
                await ctx.send(f"{member.mention} Here ya go!\nhttps://discordapp.com/channels/{guild_id}/{channel_id}")  # Send them the message!
                return

        # If we get to this point, our user isn't in a voice channel.
        await ctx.send(f"{member.mention} You aren't in a voice channel!")
        return

    @commands.command()
    @channel_check(settings.bot_managing_channel)
    async def ping(self, ctx):
        await ctx.send("Pong")

    @commands.command()
    async def aetball(self, ctx, input):
        random_phrase = random.choice(settings.aetball_list)
        await ctx.send(random_phrase)

    @commands.command()
    @channel_check(settings.bot_managing_channel)
    async def msg(self, ctx, channel_id: int, *, content):
        channel = self.bot.get_channel(channel_id)
        await channel.send(content)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send("I got {}.".format(random.choice(['heads', 'tails'])))

    @commands.command()
    async def rps(self, ctx, user_choice: str):
        valid_choices = ['rock', 'paper', 'scissors']

        if user_choice == 'Alyazia':
            await ctx.send("I picked " + random.choice(valid_choices) + ", you picked Alyazia\n**FUCK! I LOSE**")
            return

        if user_choice == 'Turkey':
            await ctx.send("I picked " + random.choice(valid_choices) + ", you picked Turkey.\n**I CAUGHT FUCKING DINNER!**")
            return

        if user_choice.lower() in valid_choices:
            bot_choice = random.choice(valid_choices)

            await ctx.send("You picked {}\nI picked {}".format(user_choice.lower(), bot_choice))

            if bot_choice == user_choice:
                await ctx.send("**It's a draw!**")
            elif bot_choice == 'scissors' and user_choice == 'rock':
                await ctx.send("**You win!**")
            elif bot_choice == 'paper' and user_choice == 'scissors':
                await ctx.send("**You win!**")
            elif bot_choice == 'rock' and user_choice == 'paper':
                await ctx.send("**You win!**")
            else:
                await ctx.send("**I win!**")
            return

        else:
            await ctx.send("Invalid choice, only accepted inputs are 'rock', 'paper', or 'scissors'.")
            return

    # @commands.command()
    # @channel_check(settings.bot_testing_channel)
    # async def die(self, ctx):
    #     await ctx.send("aw goodbye :(")
    #     quit()


def setup(bot):
    bot.add_cog(Fun(bot))
#FUCK