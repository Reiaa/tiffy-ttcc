import discord, random, config, math
from discord.ext import commands

class ClashCalculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

    @commands.command()
    async def sound(self, ctx, *args: str):
        try:
            highest_lvl = int(args[0])
        except ValueError:
            await ctx.send("First argument (highest cog level) must be an integer!\n`!sound <highest cog level> [gag 1, gag 2, ...]`")
            return
        if highest_lvl > 0 and highest_lvl < 31:
            pres_bonus = math.ceil(highest_lvl / 2.0)
        else:
            await ctx.send("Invalid cog level, accepted range is 1-30.\n`!sound <highest cog level> [gag 1, gag 2, ...]`")
            return

        toon_choices = []
        for i in range(1, len(args)):

            if args[i] not in config.sound_gags.keys():
                await ctx.send( args[i] + " is not a valid gag!\nValid gags: `'bike_horn', 'whistle', 'kazoo', 'bugle, 'aoogah', 'trunk', 'fog', 'opera'`\n`!sound <highest cog level> [gag 1, gag 2, ...]`")
                return

            toon_choices.append(args[i])

        if len(toon_choices) > 4:
            await ctx.send("Only 1-4 gag choices allowed!\n`!sound <highest cog level> [gag 1, gag 2, ...]`")
            return

        team_bonus = 1.0

        if len(toon_choices) > 1:
            team_bonus = 1.2

        raw_damage = 0
        for dmg in toon_choices:
            raw_damage += (config.sound_gags[dmg] + pres_bonus)

        total = math.ceil(raw_damage * team_bonus)
        await ctx.send("The sound combo will do **" + str(total) + "** damage.")

    @commands.command()
    async def throw(self, ctx, lure_state: str, *gags: str):
        possible_lure_states = ['lured', 'p-lured', 'unlured']
        if lure_state not in possible_lure_states:
            await ctx.send("First argument must be the lured status of the cog, `'lured', 'p-lured' or 'unlured'`\n`!throw <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
            return

        toon_choices = []

        for toon_choice in gags:
            valid_gag = (toon_choice in config.throw_gags.keys()) or (toon_choice in config.p_throw_gags.keys())
            if not valid_gag:
                await ctx.send(toon_choice + " is not a valid gag!\nValid gags: `'cupcake', 'fruit_slice', 'cream_slice', 'cake_slice, 'fruit', 'cream', 'cake', 'wedding'` if gag is prestiged, add a `p-` in front of the gag e.g. `p-cake`\n`!throw <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
                return

            toon_choices.append(toon_choice)

        if len(toon_choices) > 4:
            await ctx.send("Only 1-4 gag choices allowed!\n`!throw <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
            return

        raw_damage = 0
        for gag in toon_choices:
            if gag in config.p_throw_gags:
                raw_damage += config.p_throw_gags[gag]
            elif gag in config.throw_gags:
                raw_damage += config.throw_gags[gag]

        team_bonus = 0
        if len(toon_choices) > 1:
            team_bonus = math.ceil(raw_damage * 0.2)

        lure_bonus = 0
        if lure_state == 'lured':
            lure_bonus = math.ceil(raw_damage * 0.5)
        elif lure_state == 'p-lured':
            lure_bonus = math.ceil(raw_damage * 0.65)

        total = math.ceil(raw_damage + lure_bonus + team_bonus)
        await ctx.send("The throw combo will do **" + str(total) + "** damage.")

    @commands.command()
    async def drop(self, ctx, *gags: str):
        toon_choices = []
        for toon_choice in gags:
            if toon_choice not in config.drop_gags.keys():
                await ctx.send( toon_choice + " is not a valid gag!\nValid gags: `'flower_pot', 'sandbag', 'bowling_ball', 'anvil', 'big_weight', 'safe', 'boulder', 'piano'`")
                return

            toon_choices.append(toon_choice)

        if len(toon_choices) > 4:
            await ctx.send("Only 1-4 gag choices allowed!")
            return

        if len(toon_choices) > 1:
            drop_bonus = round(1.1 + (len(toon_choices) / 10), 3)
        else:
            drop_bonus = 1.0

        subtotal = 0
        for dmg in toon_choices:
            subtotal += config.drop_gags[dmg]

        total = math.ceil(subtotal * drop_bonus)
        await ctx.send("The drop combo will do **" + str(total) + "** damage to one cog.")

def setup(bot):
    bot.add_cog(ClashCalculator(bot))
