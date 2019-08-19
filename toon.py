from config import settings
from discord import Embed, Colour

import time
import json

class Toon:
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.claimed = False
        self.claimed_by = None
        self.claimed_at = None

    def get_name(self):
        # Gets the toons name
        return self.name

    def get_group(self):
        # Gets the toons group
        return self.group

    def set_group(self, group):
        # Modifies a toon's group
        self.group = group

    def get_status(self):
        # Gets their current claimed status
        return self.claimed, self.claimed_by

    def get_time(self):
        # Gets amount of time that toon has been claimed, returns string
        delta = round(time.time()) - self.claimed_at
        if delta < 7200:
            return "{} min ago".format(int(delta / 60))
        else:
            return "{} hours ago".format(int(delta / 3600))


    def claim(self, id):
        self.claimed = True
        self.claimed_by = id
        self.claimed_at = round(time.time())

    def unclaim(self):
        self.claimed = False
        self.claimed_by = None
        self.claimed_at = None


toons = {
    # 'name': Toon-Object
}
groups = {
    # '1a': [Toon-Object, Toon-Object, Toon-Object]
}

def add_toon(toon: Toon, modify_json=True):  # Take in Toon object, add it or our list of toons and groups

    if toon.get_name() in toons:  # Toon already exists, don't make a duplicate
        return

    if modify_json:

        toons_read.append((toon.name, toon.group))
        with open('config/toons.json', 'w') as f:
            json.dump(toons_read, f, indent=2)

    toons[toon.get_name()] = toon  # Add our toon object to the list of toons

    if toon.group in groups:  # If group exists...
        groups[toon.group].append(toon)  # Add the toon
    else:
        groups[toon.group] = [toon]  # Otherwise make a new group and add them to it

    return

def remove_toon(toon_name: str):  # Take in toon name, delete entry

    if toon_name not in toons:
        return

    toon_object = toons[toon_name] # get toon object
    toon_info = (toon_object.get_name, toon_object.get_group) # get their info
    toons_read.remove(toon_info) # remove them so we can write to json

    with open('config/toons.json', 'w') as f:
        json.dump(toons_read, f, indent=2)

    del toons[toon_name]  # remove the toon from claimable toons

    if toon_object.group in groups:

        if len(groups[toon_object.group]) is 1:  # if the toon is the only one in the group...
            del groups[toon_object.group]  # delete the group
        else:  # otherwise just remove the toon from the group.
            groups[toon_object.group].remove(toon_object)


def get_toon(toon_name: str):  # Take in toon name, return toon object
    if toon_name not in toons:
        return None
    else:
        return toons[toon_name]


with open('config/toons.json', 'r') as f:
    toons_read = json.load(f)

for toon in toons_read: # Loop through all of the toons in the settings

    toon_instance = Toon(*toon) # Create a toon object for them
    add_toon(toon_instance, modify_json=False)


initialized = False # is True if status messages exist, otherwise False
tracker_messages = {} # dictionary of tracker messages {channel_id: message}


async def update_embed(bot):
    """
    Loop through the claimed toons and find whos claimed them
    """
    claimed_toons = {}

    for toon in toons.values():
        claimed, claimed_by = toon.get_status()
        if claimed: # If the toon is claimed
            if claimed_by in claimed_toons:
                claimed_toons[claimed_by].append(toon)
            else:
                claimed_toons[claimed_by] = [toon]

    embed = Embed(
        title='Toon Statuses',
        type='rich',
        description="",
        colour=Colour.purple(),
    )

    for key in claimed_toons.keys():
        clean_names = result = "\n".join([t.get_name() for t in claimed_toons[key]])
        fetched_name = await bot.fetch_user(key)
        embed.add_field(name=fetched_name, value=clean_names, inline=True)
        claim_times = "\n".join([t.get_time() for t in claimed_toons[key]])
        embed.add_field(name="Time Claimed", value=claim_times, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True) # Creates an empty field in 3rd column, embeds don't support 2 columns for inline fields, or I'm just dumb that too

    if len(claimed_toons.keys()) == 0:
        embed.set_footer(text="No toons are currently online")
    else:
        embed.set_footer(text="Times are automatically updated every minute")

    global initialized
    global tracker_messages

    if initialized:
        for channel_id in settings.toon_status_channels:
            msg = tracker_messages[channel_id]
            await msg.edit(embed=embed)
    else:
        for channel_id in settings.toon_status_channels:
            channel = bot.get_channel(channel_id)
            tracker_messages[channel_id] = await channel.send(embed=embed)

        initialized = True


async def check_if_toon_claimed(toon_name):
    return toons[toon_name].claimed, toons[toon_name].claimed_by

async def check_if_group_claimed(group_name, discord_user):
    list_of_toons = groups[group_name] # Gets the list of toon objects
    i = 0
    for toon in list_of_toons:
        if toon.claimed:
            i += 1
            if toon.claimed_by != discord_user.id:
                return True
    if i >= 4: return True

async def check_if_user_has_claimed(discord_user):
    for toon in toons.values():
        if toon.claimed_by == discord_user.id:
            return True
    return False


async def claim_toon(name, discord_user):
    toons[name].claim(discord_user.id)

async def unclaim_toon(name, discord_user):
    toons[name].unclaim()

async def claim_group(name, discord_user):
    for toon in groups[name]:
        toon.claim(discord_user.id)

async def unclaim_group(name, discord_user):
    for toon in groups[name]:
        toon.unclaim()

async def unclaim_all(discord_user):
    for toon in toons.values():
        if toon.claimed_by == discord_user.id:
            toon.unclaim()
