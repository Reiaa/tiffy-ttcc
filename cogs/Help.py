from config import settings
from discord import Colour, Embed
from discord.ext import commands

claiming_help_embed = Embed(
    title="Toon Claiming Help",
    type='rich',
    description='',
    colour=Colour.red(),
)

general_help_embed = Embed(
    title="Commands",
    type="rich",
    description='',
    colour=Colour.blue(),
)

gags_embed = Embed(
    title='Gags',
    type='rich',
    description='',
    colour=Colour.dark_blue()
)

# Claiming Help --------------------------------------------------
claiming_help_embed.add_field(
    name='!claim',
    value="Claim a toon or group of toons. e.g. `!claim zen` or `!claim 2x`",
    inline=True
)

claiming_help_embed.add_field(
    name='!unclaim',
    value="Unclaim a toon, group of toons, or all toons. e.g. `!unclaim all`",
    inline=True
)

claiming_help_embed.add_field(
    name='!forceclaim',
    value="Forcefully claim toons for someone else. e.g. `!forceclaim @devvy#3579 lament`",
    inline=True
)

claiming_help_embed.add_field(
    name='!forceunclaim',
    value="Forcefully unclaim all/some toons from someone else. e.g. `!forceunclaim @devvy#3579 all`",
    inline=True
)

claiming_help_embed.add_field(
    name='!nickname',
    value="Set a nickname for a toon. e.g. `!nickname furrtastic kitteneer = furr`",
    inline=True
)

claiming_help_embed.add_field(
    name='!nicknames',
    value="See a list of all nicknames currently stored.",
    inline=True
)

# General Help -----------------------------------------------------------
general_help_embed.add_field(
    name='!calc',
    value='Calculate the amount of damage a gag combo would do to a single cog on TTCC\nUsage: `!calc <cog level> <lure state> [gag 1, gag 2, gag 3...]`',
    inline=False
)

general_help_embed.add_field(
    name='!gags',
    value='Show a list of valid names for gags used for the gag calculator',
    inline=False
)

#Gags Embed -------------------------------------------------------------
gags_embed.add_field(
    name="Trap",
    value="`banana_peel`, `rake`, `spring`, `marbles`, `quicksand`, `trap_door`, `wrecking_ball`, `tnt`"
)

gags_embed.add_field(
    name="Lure",
    value="`lure`"
)

gags_embed.add_field(
    name="Sound",
    value="`bike_horn`, `whistle`, `kazoo`, `bugle`, `aoogah`, `trunk`, `fog`, `opera`"
)

gags_embed.add_field(
    name="Squirt",
    value="`squirting_flower`, `glass_of_water`, `squirt_gun`,  `water_balloon`, `seltzer_bottle`, `fire_hose`, `storm_cloud`, `geyser`"
)

gags_embed.add_field(
    name="Zap",
    value="`joy_buzzer`, `carpet`, `balloon`, `kart_battery`, `taser`, `tv`, `tesla`, `lightning`"
)

gags_embed.add_field(
    name="Throw",
    value="`cupcake`, `fruit_slice`, `cream_slice`, `cake_slice`, `fruit`, `cream`, `cake`, `wedding`"
)

gags_embed.add_field(
    name="Drop",
    value="`flower_pot`, `sandbag`, `bowling_ball`, `anvil`, `big_weight`, `safe`, `boulder`, `piano`"
)

gags_embed.set_footer(text="A gag can be 'prestiged' by typing the gag name in all caps: inputting `CAKE` -> prestiged cake")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        channel_id = ctx.channel.id

        with open('config/valid_claiming_channels', 'r') as f:
            valid_claiming_channels = json.load(f)

        if channel_id in valid_claiming_channels:
            await ctx.send(embed=claiming_help_embed)

        else:
            await ctx.send(embed=general_help_embed)

    @commands.command()
    async def gags(self, ctx):
        channel_id = ctx.channel.id

        with open('config/valid_claiming_channels', 'r') as f:
            valid_claiming_channels = json.load(f)

        if channel_id not in valid_claiming_channels:
            await ctx.send(embed=gags_embed)


def setup(bot):
    bot.add_cog(Help(bot))
