import discord
import toon
import json

from toon import Toon
from config import settings
from discord.ext import commands, ui

CONFIRM = 'Confirm'
CANCEL = 'Cancel'

confirm_choices = [
    ui.Choice(CONFIRM, button='✅'),
    ui.Choice(CANCEL, button='❌')
]

def channel_check():
    def predicate(ctx):
        with open('config/valid_claiming_channels.json', 'r') as f:
            valid_channels = json.load(f)
        return (ctx.message.channel.id in valid_channels)
    return commands.check(predicate)


class ToonClaimer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currently_modifying_toons = []

        with open ('config/toons.json', 'r') as f:
            self.toons_to_write = json.load(f)  # We only use this to update our json file when someone edits or adds a toon

        with open('config/toon_nicknames.json', 'r') as f:
            self.toon_nicknames = json.load(f)

        with open('config/valid_claiming_channels.json', 'r') as f:
            self.valid_claiming_channels = json.load(f)


    async def set_nickname(self, toon_name: str, nickname: str): # return false if failed
        toon_name = toon_name.title()
        nickname = nickname.title()

        if toon_name not in toon.toons.keys():
            return False, 'ToonNotFound'
        elif nickname.lower() in toon.groups.keys():
            return False, 'NameIsGroup'
        else:
            self.toon_nicknames[nickname] = toon_name
            with open('config/toon_nicknames.json', 'w') as f:
                json.dump(self.toon_nicknames, f, indent=2)
            return True, 'Yay'


    async def claim_toons(self, member: discord.Member, toons: list):
        msg = f"{member.mention}\n"  # This is the message we will send to the user at the end

        for name in toons:  # Loop through all toons provided in command argument
            if name in self.toon_nicknames.keys():  # Check if a nickname was given
                name = self.toon_nicknames[name]  # If nickname was given, convert our toon name to represent the correct toon

            if name in toon.toons.keys():
                is_claimed, claimed_by = await toon.check_if_toon_claimed(name)
                if is_claimed:
                    msg += f':x: The toon `{name}` is already claimed!\n'
                    continue
                else:
                    msg += f':white_check_mark: Claimed the toon `{name}`!\n'
                    await toon.claim_toon(name, member)
                    continue

            elif name.lower() in toon.groups.keys():
                if await toon.check_if_group_claimed(name.lower(), member):
                    msg += f':x: One or more toons in the group `{name.lower()}` are currently claimed!\n'
                    continue
                else:
                    msg += f':white_check_mark: Claimed the group `{name.lower()}`!\n'
                    await toon.claim_group(name.lower(), member)
                    continue

            else:
                msg += f':question: The toon/group `{name}` does not exist!\n'
                continue

        await toon.update_embed(self.bot)
        return msg

    async def unclaim_toons(self, member: discord.Member, toons: list):
        msg = f"{member.mention}\n"  # This is the message we will send to the user at the end

        for name in toons:  # Loop through all toons provided in command argument
            if name in self.toon_nicknames.keys():  # Check if a nickname was given
                name = self.toon_nicknames[name]  # If nickname was given, convert our toon name to represent the correct toon

            if name in toon.toons.keys():
                is_claimed, claimed_by = await toon.check_if_toon_claimed(name)
                if not is_claimed:
                    msg += f':x: The toon `{name}` is not claimed!\n'
                    continue
                elif is_claimed and claimed_by != member.id:
                    msg += f':x: You cannot unclaim the toon `{name}`! They are claimed by another member.'
                    continue
                else:
                    msg += f':white_check_mark: Unclaimed the toon `{name}`!\n'
                    await toon.unclaim_toon(name, member)
                    continue

            elif name.lower() in toon.groups.keys():
                if not await toon.check_if_group_claimed(name.lower(), member):
                    msg += f':x: One or more toons in the group `{name.lower()}` are not claimed by you!\n'
                    continue
                else:
                    msg += f':white_check_mark: Unclaimed the group `{name.lower()}`!\n'
                    await toon.unclaim_group(name.lower(), member)
                    continue

            else:
                msg += f':question: The toon/group `{name}` does not exist!\n'
                continue

        await toon.update_embed(self.bot)
        return msg

    async def unclaim_all_toons(self, member: discord.Member):
        msg = f"{member.mention}\n"

        if await toon.check_if_user_has_claimed(member):

            await toon.unclaim_all(member)
            await toon.update_embed(self.bot)

            msg += ":white_check_mark: Unclaimed all of your toons!"
        else:
            msg += ":question: You have no toons claimed!"

        return msg

    # Channel setting commands (admins)

    @commands.command(aliases=['set'])
    @commands.has_permissions(manage_channels=True)
    async def set_claiming_channel(self, ctx):

        channel_id = ctx.message.channel.id

        if channel_id in self.valid_claiming_channels:
            await ctx.send(f"{ctx.author.mention} This channel already allows toon claiming!")
            return

        decision = await ui.select(ctx, f'{ctx.author.mention} Are you sure you want to allow toon claiming in this channel?', confirm_choices)

        if decision is CANCEL:
            await ctx.send(f"{ctx.author.mention} Cancelled!")
            return



        self.valid_claiming_channels.append(channel_id)

        with open('config/valid_claiming_channels.json', 'w') as f:
            json.dump(self.valid_claiming_channels, f)

        await ctx.send(f"{ctx.author.mention} Users can now claim toons in this channel!\nUse `!remove` to undo")
        return

    @commands.command(aliases=['remove'])
    @commands.has_permissions(manage_channels=True)
    async def remove_claiming_channel(self, ctx):

        channel_id = ctx.message.channel.id

        if channel_id not in self.valid_claiming_channels:
            await ctx.send(f"{ctx.author.mention} This channel isn't set as a claiming channel! To set it as one, use `!set`")
            return

        decision = await ui.select(ctx, f"{ctx.author.mention} Are you sure you want to remove this channel as a claiming channel?", confirm_choices)

        if decision is CANCEL:
            await ctx.send(f"{ctx.author.mention} Cancelled!")
            return

        self.valid_claiming_channels.remove(channel_id)

        with open('config/valid_claiming_channels.json', 'w') as f:
            json.dump(self.valid_claiming_channels, f)

        await ctx.send(f"{ctx.author.mention} Removed this channel. To add it back, use `!set`")
        return

    # Toon management commands (admins)

    @commands.command(aliases=['create'])
    @commands.has_permissions(administrator=True)
    @channel_check()
    async def createtoon(self, ctx):  # add toon object to toon.py, group assignment and json stuff is handled there as well.

        if ctx.author.id in self.currently_modifying_toons:
            await ctx.send(f"{ctx.author.mention} Slow down! You are already currently modifying toons.")
            return
        else:
            self.currently_modifying_toons.append(ctx.author.id)

        name = None
        group = None

        # First, we need to get information from the user, we will do this by having a list [toon name, group]
        while name is None:
            name = await ui.prompt(ctx, 'What is the name of the toon?')
            name = name.title() # Fix capitalization since that is our format
            if name in toon.toons.keys():  # Toon already exists, we can't create it
                decision = await ui.select(ctx, f'The toon `{name}` already exists! Try again?', confirm_choices)  #See if user wants to try again
                if decision is CONFIRM:
                    name = None  # Set name to none and go through the loop again
                    continue
                else:
                    await ctx.send('Cancelled toon creation.')  # Cancel the command process
                    self.currently_modifying_toons.remove(ctx.author.id)
                    return

            # Make sure the user is okay with the name.
            decision = await ui.select(ctx, f'Are you sure you would like to create the toon `{name}`?', confirm_choices)
            if decision is CANCEL:
                decision = await ui.select(ctx, f'Do you want to start over?', confirm_choices)  #See if user wants to try again
                if decision is CONFIRM:
                    name = None  # Set name to none and go through the loop again
                    continue


        # Okay, now we have the name, lets get the toons group
        while group is None:
            group = await ui.prompt(ctx, 'What group would you like the toon to be apart of?\nType `none` if you do not want the toon to have a group.\nType `cancel` if you change your mind.')
            group = group.lower()  # Our group format is lowercase

            if group == 'none':  # We will add the toon to our 'misc' group that cant be claimed
                break

            if group == 'cancel':
                await ctx.send('Cancelled toon creation.')
                self.currently_modifying_toons.remove(ctx.author.id)
                return

            if group in toon.groups.keys():  # Group exists, we are adding the toon to the group rather than making a new one
                decision = await ui.select(ctx, f'Are you sure you want to add `{name}` to the group {group}?', confirm_choices)
                if decision is CANCEL:
                    group = None  # User doesn't want to add to group, start over
                    continue
            else:  # Group didn't exist, we are going to end up making a new one
                decision = await ui.select(ctx, f"Are you sure you want to make a new group called `{group}` and add `{name}` to it?", confirm_choices)
                if decision is CANCEL:
                    group = None
                    continue

        # Now we have our toon name and group, lets make sure they are sure
        decision = await ui.select(ctx, f"You are about to create the toon `{name}` in group `{group}`, If you cancel, you will need to start over.", confirm_choices)
        if decision is CANCEL:
            await ctx.send('Cancelled toon creation.')
            self.currently_modifying_toons.remove(ctx.author.id)
            return


        # First we define our toon's info in order to make the toon object
        toon_info = (name, group)

        # Next we want to make the toon object and add it to our toons for immediate use
        toon_instance = Toon(*toon_info)
        toon.add_toon(toon_instance)

        # Done, toon should be created!
        await ctx.send(f'{ctx.author.mention} Added the toon `{name}` in group `{group}`')
        self.currently_modifying_toons.remove(ctx.author.id)
        return



    @commands.command(aliases=['edit'])
    @commands.has_permissions(administrator=True)
    @channel_check()
    async def edittoon(self, ctx):  # change toons group in toon.py and show change in json file
        pass

    @commands.command(aliases=['delete'])
    @commands.has_permissions(administrator=True)
    @channel_check()
    async def removetoon(self, ctx):

        if ctx.author.id in self.currently_modifying_toons:
            await ctx.send(f"{ctx.author.mention} Slow down! You are already currently modifying toons.")
            return
        else:
            self.currently_modifying_toons.append(ctx.author.id)

        name = None

        while name is None:
            name = await ui.prompt(ctx, 'What is the name of the toon you would like to delete?\nType `cancel` if you change your mind.')
            name = name.title()  # again, follow the format

            if name not in toon.toons.keys():
                decision = await ui.select(ctx, f"Toon `{name}` doesn't exist! Try again?", confirm_choices)

                if decision is CONFIRM:
                    name = None
                    continue
                else:
                    await ctx.send('Cancelled toon deletion.')
                    self.currently_modifying_toons.remove(ctx.author.id)
                    return

        # We got the toon, make sure they want to delete them.
        decision = await ui.select(ctx, f"Are you sure you want to delete the toon `{name}`? (WARNING: This cannot be undone, you must recreate the toon upon deletion.)", confirm_choices)

        if decision is CANCEL:
            await ctx.send('Cancelled toon deletion.')
            self.currently_modifying_toons.remove(ctx.author.id)
            return

        toon.remove_toon(name)  # This function will handle all the deleting and json editing.

        await ctx.send(f'{ctx.author.mention} Deleted the toon `{name}`')
        self.currently_modifying_toons.remove(ctx.author.id)
        return



    # Toon claiming commands (everyone)

    @commands.command(aliases=['c'])
    @channel_check()
    async def claim(self, ctx, *, input: str):

        input = input.title()  # This fixes capitalization for the user automatically, makes their life easier
        toons_to_claim = [name.strip() for name in input.split(',')]  # separate our user's inputs into separate indeces of a list. list is all the names they want to claim

        msg = await self.claim_toons(ctx.author, toons_to_claim)
        await ctx.send(msg)

    @commands.command(aliases=['u', 'un', 'uclaim'])
    @channel_check()
    async def unclaim(self, ctx, *, input: str):

        if input == 'all'.casefold():  # Lets make a case for unclaiming all here so we don't have to run the entire code every time. (also most common unclaiming method)
            await ctx.send(await self.unclaim_all_toons(ctx.author))
            return

        input = input.title()  # This fixes capitalization for the user automatically, makes their life easier
        toons_to_unclaim = [name.strip() for name in input.split(',')]  # separate our user's inputs into separate indeces of a list. list is all the names they want to unclaim

        msg = await self.unclaim_toons(ctx.author, toons_to_unclaim)
        await ctx.send(msg)

    @commands.command(aliases=['fclaim', 'fc', 'forcec'])
    # @commands.has_permissions(manage_server=True)  # uncomment this line if you want only admins to forceunclaim
    @channel_check()
    async def forceclaim(self, ctx, discord_user: discord.Member, *, input: str):

        input = input.title()  # This fixes capitalization for the user automatically, makes their life easier
        toons_to_claim = [name.strip() for name in input.split(',')]  # separate our user's inputs into separate indeces of a list. list is all the names they want to claim

        await ctx.send(f"{await self.claim_toons(discord_user, toons_to_claim)} (forced by {ctx.author.mention})")


    @commands.command(aliases=['funclaim', 'fu', 'forceu'])
    # @commands.has_permissions(manage_server=True)  # uncomment this line if you want only admins to forceunclaim
    @channel_check()
    async def forceunclaim(self, ctx, discord_user: discord.Member, *, input: str):

        if input == 'all'.casefold():
            await ctx.send(f"{await self.unclaim_all_toons(discord_user)} (forced by {ctx.author.mention})")
            return

        input = input.title()  # This fixes capitalization for the user automatically, makes their life easier
        toons_to_unclaim = [name.strip() for name in input.split(',')]  # separate our user's inputs into separate indeces of a list. list is all the names they want to unclaim

        await ctx.send(f"{await self.unclaim_toons(discord_user, toons_to_unclaim)} (forced by {ctx.author.mention})")

    @commands.command(aliases=['nick', 'n'])
    @channel_check()
    async def nickname(self, ctx, *, input: str):

        if '=' not in ctx.message.content:
            await ctx.send(f"{ctx.author.mention} You must specifiy a nickname with an equal sign! e.g. `!nickname xarius pendragon = lou`")
            return

        toon_and_nick = [name.strip() for name in input.split('=')]  # name refers to the actual name and new nickname, our end result SHOULD be ['xarius pendragon', 'lou']
        if len(toon_and_nick) is not 2:
            await ctx.send(f"{ctx.author.mention} Slow down! There should only be one equal sign in your command. `!nickname toon = nickname`")
            return

        toon, nickname = toon_and_nick[0], toon_and_nick[1]

        is_successful, error = await self.set_nickname(toon, nickname)

        if not is_successful:
            if error is 'ToonNotFound':
                await ctx.send(f"{ctx.author.mention} `{toon.title()}` is not a valid toon!")
                return
            elif error is 'NameIsGroup':
                await ctx.send(f"{ctx.author.mention} `{nickname}` is a group! Toon nicknames can't be groups!")
                return
        else:
            await ctx.send(f"{ctx.author.mention} :white_check_mark: `{toon.title()}` can now be referred to as `{nickname.title()}`!")

    @commands.command(aliases=['nicks'])
    @channel_check()
    async def nicknames(self, ctx):
        embed = discord.Embed(
            title='Nicknames',
            type='rich',
            description="",
            colour=discord.Colour.purple(),
        )
        name_with_all_nicks = {}
        for nickname, toon_name in self.toon_nicknames.items():
            if toon_name not in name_with_all_nicks:
                name_with_all_nicks[toon_name] = [nickname]
            else:
                name_with_all_nicks[toon_name].append(nickname)

        name_with_all_nicks = dict(sorted(name_with_all_nicks.items()))

        for toon_name, list_of_nicks in name_with_all_nicks.items():
            if len(list_of_nicks) > 1:
                to_string = ', '.join(list_of_nicks)
            else:
                to_string = list_of_nicks[0]
            embed.add_field(
                name=toon_name,
                value=to_string,
                inline=False
            )

        await ctx.send(embed=embed)



    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):

        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(err, commands.MissingPermissions):
            await ctx.send("{} you don't have permission to use that command!".format(ctx.message.author.mention))
        elif isinstance(err, commands.BadArgument):
            await ctx.send("{} One of your arguments were incorrect! refer to `!help`".format(ctx.message.author.mention))
        elif isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("{} You are missing some required arguments! refer to `!help`".format(ctx.message.author.mention))
        else:
            print("(COMMAND ERROR) {} issued command in {} ({}) that raised error: {}".format(ctx.author, ctx.message.channel, ctx.message, err))


def setup(bot):
    bot.add_cog(ToonClaimer(bot))
