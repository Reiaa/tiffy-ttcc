import math

from config import settings
from discord.ext import commands


class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author is self.bot.user:
            return

    @commands.command()
    async def calc(self, ctx, *args):

        possible_lure_states = ['lured', 'p-lured', 'unlured']

        toon_choices = []  # this will be a list of dictionaries containing unordered attacks, we sort later
        cog_level = 1  # default value if one isn't provided
        initial_lure_state, lure_state = 'unlured', 'unlured'  # default value if one isn't provided

        if len(args) is 0:
            await ctx.send("No arguments provided, you may input either a cog level, initial lure state, or a gag as a"
                           " valid argument. Order does not matter.\nTo see a list of valid gags, use !gags\nValid cog"
                           " levels are 1-30\nValid initial lure states are 'lured' and 'p-lured'; if left blank,"
                           " calculator assumes unlured.\nFor more info use !help")  # TODO: make multiline string
            return

        gags = settings.all_gags

        for arg in args:  # set our arguments, args can be in any order
            if arg.lower() in gags.keys():  # add a gag
                gag = arg.lower()
                gag_info = gags[gag]  # this is a tuple that stores (dmg, track_number)
                attack = {'gag': arg,
                          'dmg': gag_info[0],
                          'track': gag_info[1]}  # our attack will be a dictionary with name of gag, and its track
                toon_choices.append(attack)
            elif arg.lower() in possible_lure_states:  # set a lure state
                initial_lure_state, lure_state = arg, arg
            else:
                try:
                    cog_level = int(arg)
                except ValueError:
                    await ctx.send(f"`{arg}` is an invalid argument")
                    return

        if cog_level > 30 or cog_level < 1:
            await ctx.send("Cog level must be between level 1-30!")
            return

        if len(toon_choices) > 4:
            await ctx.send("Only 1-4 gag choices allowed!")
            return

        sorted_toon_choices = sorted(toon_choices, key=lambda k: k['track'])  # sort our gags by order of track

        # Now that our gags are sorted, let's loop through the gags and calculate damage
        # Our gags are stored as dictionaries in a sorted list by track order
        # sorted_toon_choices['gag'] = name of the gag
        # sorted_toon_choices['dmg'] = damage of gag
        # sorted_toon_choices['track'] = track number

        total_damage = 0  # this is the value that we print at the end to the user
        track_damages = {}  # key is track number, value is total accumulated damage from that track
        track_frequency = {}  # key is track number, value is num of attacks in that track - 1, i.e. 2 attacks will be a value of 1.
                              # We do this because our combo damage multipliers are stored as lists, and we call the multiplier by its index

        trap_hit = False  # we use this so we know whether or not to count trap damage toward our total cog damage
        cog_soaked = False  # this is used so we know whether or not to multiply a zap gags damage by 3

        for attack in sorted_toon_choices:  # go through our dictionaries to determine the 'frequency' of each track

            if attack['track'] not in track_frequency:
                track_frequency[attack['track']] = 0
            else:
                track_frequency[attack['track']] += 1

        current_track_number = {}  # key is attack's track, value is current attack's 'turn' in matching tracks. i.e. if
                                   # two toons use trap, the first trap will have a key of 0, and the second a key of 1.
                                   # This is used first of all so we can know when to calculate team bonus damage, and
                                   # to know whether or not to cancel out trap damage because of double trapping.

        # We will define our tracks to have corresponding names for easier readability
        # Our variables that we set are really just integers that go from 0-6
        TRAP = settings.TRAP
        LURE = settings.LURE
        SOUND = settings.SOUND
        SQUIRT = settings.SQUIRT
        ZAP = settings.ZAP
        THROW = settings.THROW
        DROP = settings.DROP

        for attack in sorted_toon_choices:  # loop through every gag, and calculate the damage done to the cog
            if attack['track'] not in current_track_number:
                current_track_number[attack['track']] = 0
            else:
                current_track_number[attack['track']] += 1

            if attack['track'] is TRAP:
                if lure_state != 'unlured':
                    await ctx.send("You tried to trap on an already lured cog!")
                    return
                elif current_track_number[attack['track']] is 0:
                    if attack['gag'].isupper():
                        track_damages[attack['track']] = attack['dmg'] + (3 * cog_level)
                    else:
                        track_damages[attack['track']] = attack['dmg']
                else:  # double trap, cancel damage
                    track_damages[attack['track']] = 0

            if attack['track'] is LURE:
                if initial_lure_state != 'unlured':
                    await ctx.send("You tried to lure an already lured cog!")
                    return
                elif TRAP in track_damages.keys():
                    if track_damages[TRAP] > 0:
                        trap_hit = True
                        lure_state = 'unlured'
                elif attack['gag'] == 'lure' and lure_state != 'p-lured':
                    lure_state = 'lured'
                elif attack['gag'].isupper():
                    lure_state = 'p-lured'

            if attack['track'] is SOUND:
                bonus_damage = 0
                if attack['track'] not in track_damages:
                    if attack['gag'].isupper():
                        track_damages[attack['track']] = (attack['dmg'] + math.ceil(0.5 * cog_level))
                    else:
                        track_damages[attack['track']] = attack['dmg']
                else:
                    if attack['gag'].isupper():
                        track_damages[attack['track']] += (attack['dmg'] + math.ceil(0.5 * cog_level))
                    else:
                        track_damages[attack['track']] += attack['dmg']
                if current_track_number[attack['track']] == track_frequency[attack['track']]:
                    bonus_damage = math.ceil(track_damages[attack['track']] * settings.combo_bonuses[track_frequency[attack['track']]] * 0.01)
                track_damages[attack['track']] += bonus_damage
                lure_state = 'unlured'

            if attack['track'] is THROW or attack['track'] is SQUIRT:
                bonus_damage = 0
                lure_bonus_damage = 0
                if attack['track'] is SQUIRT and not cog_soaked:
                    cog_soaked = True
                if attack['track'] not in track_damages:
                    if attack['gag'].isupper() and attack['track'] is THROW:
                        track_damages[attack['track']] = attack['dmg'] + math.ceil(attack['dmg'] * 0.1)
                    else:
                        track_damages[attack['track']] = attack['dmg']
                else:
                    if attack['gag'].isupper() and attack['track'] is THROW:
                        track_damages[attack['track']] += attack['dmg'] + math.ceil(attack['dmg'] * 0.1)
                    else:
                        track_damages[attack['track']] += attack['dmg']
                if current_track_number[attack['track']] == track_frequency[attack['track']]:
                    bonus_damage = math.ceil(track_damages[attack['track']] * settings.combo_bonuses[track_frequency[attack['track']]] * 0.01)
                    if lure_state == 'lured':
                        lure_bonus_damage = math.ceil(track_damages[attack['track']] * 0.5)
                    elif lure_state == 'p-lured':
                        lure_bonus_damage = math.ceil(track_damages[attack['track']] * 0.65)
                    lure_state = 'unlured'
                track_damages[attack['track']] += bonus_damage
                track_damages[attack['track']] += lure_bonus_damage

            if attack['track'] is ZAP:
                soak_multiplier = 1
                if cog_soaked:
                    soak_multiplier = 3
                if attack['track'] not in track_damages:
                    track_damages[attack['track']] = attack['dmg'] * soak_multiplier
                else:
                    track_damages[attack['track']] += attack['dmg'] * soak_multiplier

                lure_state = 'unlured'

            if attack['track'] is DROP:
                if lure_state == 'unlured':
                    bonus_damage = 0
                    if attack['track'] not in track_damages:
                        track_damages[attack['track']] = attack['dmg']
                    else:
                        track_damages[attack['track']] += attack['dmg']
                    if current_track_number[attack['track']] == track_frequency[attack['track']]:
                        bonus_damage = math.ceil(track_damages[attack['track']] * settings.drop_combo_bonuses[track_frequency[attack['track']]] * 0.01)

                    track_damages[attack['track']] += bonus_damage

        for track in track_damages:
            if track is TRAP and not trap_hit:
                continue
            total_damage += track_damages[track]

        total = math.ceil(total_damage)
        await ctx.send(f"The total damage is **{total}** on a level `{cog_level}` cog.")


def setup(bot):
    bot.add_cog(Calculator(bot))
