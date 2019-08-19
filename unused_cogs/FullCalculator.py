import discord, random, config, math
from discord.ext import commands

class FullCalculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

    @commands.command()
    async def calculate(self, ctx, lure_state: str, *gags: str):
        possible_lure_states = ['lured', 'p-lured', 'unlured']
        if lure_state not in possible_lure_states:
            await ctx.send("First argument must be the lured status of the cog, `'lured', 'p-lured' or 'unlured'`\n`!calculate <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
            return

        toon_choices = []

        for toon_choice in gags:
            valid_gag = toon_choice in config.all_gags.keys()
            if not valid_gag:
                await ctx.send(toon_choice + " is not a valid gag!\nValid gags: " + str(config.all_gags.keys()) + " \n`!calculate <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
                return

            toon_choices.append(toon_choice)

        if len(toon_choices) > 4:
            await ctx.send("Only 1-4 gag choices allowed!\n`!calculate <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
            return

        total_damage = 0
        track_damages = {}
        track_numbers = {}
        trap_exists = False
        for gag in toon_choices:
		    if gag[1] not in track_numbers:
                track_numbers[gag[1]] = 0
            else:
                track_numbers[gag[1]] += 1
				
        current_track_number = {}

        for gag in toon_choices:
		
            if gag[1] not in current_track_number:
                current_track_number[gag[1]] = 0
            else:
                current_track_number[gag[1]] += 1

            if gag[1] == 'TRAP':
                if lure_state != 'unlured':
	                await ctx.send("You tried to trap on an already lured cog!\n`!calculate <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
                elif current_track_number[gag[1]] == 0:
                    track_damages[gag[1]] = gag[0]
                else: #double trap, cancel damage
                    track_damages[gag[1]] = 0
					
            if gag[1] == 'LURE':
                if lure_state != 'unlured':
	                await ctx.send("You tried to lure an already lured cog!\n`!calculate <lured | p-lured | unlured> [gag 1, gag 2, ...]`")
                elif 'TRAP' in track_damages:
		            trap_hit = True
                elif gag[0] == 'lure' and lure_state != 'p-lured':
                    lure_state = 'lured'
                elif gag[0] == 'p-lure'
                    lure_state == 'p-lured'
					
            if gag[1] == 'SOUND':
                bonus_damage = 0
                if gag[1] not in track_damages:
                    track_damages[gag[1]] = 0
                else:
                    track_damages[gag[1]] += gag[0]
                if current_track_number[gag[1]] == track_numbers[gag[1]]:
                    bonus_damage = math.ceil[track_damages[gag[1] * config.combo_bonuses[track_numbers[gag[1]]]]
                track_damages[gag[1]] += bonus_damage
                lure_state = 'unlured'
				
            if gag[1] == 'THROW' or gag[1] == 'SQUIRT':
                bonus_damage = 0
                lure_bonus_damage = 0
                if gag[1] not in track_damages:
                    track_damages[gag[1]] = 0
                else:
                    track_damages[gag[1]] += gag[0]
                if current_track_number[gag[1]] == track_numbers[gag[1]]:
                    bonus_damage = math.ceil[track_damages[gag[1] * config.combo_bonuses[track_numbers[gag[1]]]]
                    if lure_state == 'lured':
                        lure_bonus_damage = math.ceil[track_damages[gag[1]] * 0.5]
                    elif lure_state == 'p-lured':
                        lure_bonus_damage = math.ceil[track_damages[gag[1]] * 0.65]
                    lure_state = 'unlured'
                track_damages[gag[1]] += bonus_damage
                track_damages[gag[1]] += lure_bonus_damage
				
            if gag[1] == 'DROP':
                if lure_state == 'unlured':
                    bonus_damage = 0
                    if gag[1] not in track_damages:
                        track_damages[gag[1]] = 0
                    else:
                        track_damages[gag[1]] += gag[0]
                    if current_track_number[gag[1]] == track_numbers[gag[1]]:
                        bonus_damage = math.ceil[track_damages[gag[1] * config.drop_combo_bonuses[track_numbers[gag[1]]]]
                    track_damages[gag[1]] += bonus_damage
                
        for track in track_damages:
            total_damage += track

        total = math.ceil(total_damage)
        await ctx.send("The total damage is **" + str(total) + "** damage.")

def setup(bot):
    bot.add_cog(FullCalculator(bot))
