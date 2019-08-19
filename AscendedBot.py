import json
import os

from config import settings
from discord.ext import commands


def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)


bot = commands.Bot(command_prefix='!')
bot.remove_command('help')


@bot.event
async def on_ready():
    print("Logged in successfully as {0.user}".format(bot))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


# commands to handle cogs (extensions)
@bot.command()
@channel_check(settings.bot_managing_channel)
async def unload(ctx, cog):
    try:
        bot.unload_extension("cogs.{}".format(cog))
        await ctx.send("`{}` extension was disabled".format(cog))
    except Exception as error:
        await ctx.send("`{}` could not be unloaded: {}".format(cog, error))


@bot.command()
@channel_check(settings.bot_managing_channel)
async def load(ctx, cog):
    try:
        bot.load_extension("cogs.{}".format(cog))
        await ctx.send("`{}` extension was enabled".format(cog))
    except Exception as error:
        await ctx.send("`{}` could not be loaded: {}".format(cog, error))


@bot.command()
@channel_check(settings.bot_managing_channel)
async def reload(ctx, cog):
    try:
        await ctx.send("Reloading `{}` extension...".format(cog))
        bot.unload_extension("cogs.{}".format(cog))
        bot.load_extension("cogs.{}".format(cog))
        await ctx.send("Successfully reloaded `{}` extension!".format(cog))
    except Exception as error:
        await ctx.send("Failed to reload `{}` extension!\n`{}`".format(cog, error))

# Make sure required json files are generated
for file in settings.required_json_files:
    try:
        with open(file, 'r') as f:
            print(f'- {file} exists!')
    except FileNotFoundError:
        with open(file, 'w') as f:
            json.dump([], f)
            print(f'- {file} did not exist, creating a blank one')

# Enables extensions on bot startup
for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        try:
            cog = 'cogs.' + cog[:-3]
            bot.load_extension(cog)
            print("Loaded '{}' cog successfully".format(cog))
        except Exception as error:
            print("{} could not be loaded: {}".format(cog, error))

# Make sure that you have a file in your 'config' folder named 'token.txt' with your bot's token inside
try:
    with open('config/token.txt', 'r') as f:
        bot.run(f.read())
except FileNotFoundError:
    input('[FATAL]: "token.txt" does not exist! Make sure you make a txt file in the "config" folder containing your bots token!')

