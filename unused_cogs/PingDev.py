import discord, asyncio, random, config
from discord.ext import commands


def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

class PingDev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ping_channel = self.bot.get_channel(571815383430987776)
        self.bot_testing_channel = self.bot.get_channel(557395184577544222)
        self.loop_running = False
        self.members_with_perms = []
        self.ignored_members = ['179062392913788928', '566196780283461632', '334282153204514816', '497361011926630400'] #dev, the alys, and bot


    async def update_members_with_perms(self):
        for member in self.ping_channel.members:
            if str(member.id) in self.ignored_members:
                pass
            elif self.ping_channel.overwrites_for(member).send_messages:
                if member in self.members_with_perms:
                    pass
                else:
                    self.members_with_perms.append(member)
            elif member in self.members_with_perms:
                self.members_with_perms.remove(member)

    @commands.command()
    @channel_check(config.bot_testing_channel)
    async def startpermloop(self, ctx):
        self.loop_running = True

        while self.loop_running:

            await PingDev.update_members_with_perms(self)

            for member in self.ping_channel.members:

                if str(member.id) in self.ignored_members:
                    pass
                elif self.ping_channel.overwrites_for(member).send_messages:            #if member can send messages in the channel, remove that permission
                    await self.ping_channel.set_permissions(member, send_messages=None)
                    await self.bot_testing_channel.send("{} can no longer send messages in ping channel".format(str(member)))
                else:
                    if random.randint(1,20) == 20:                  # 5% chance for a user to be selected to have perms to spam dev
                        await self.ping_channel.set_permissions(member, send_messages=True)
                        await self.bot_testing_channel.send("{} can now send messages in the ping channel for an hour".format(str(member)))

            await PingDev.update_members_with_perms(self)

            for member in self.members_with_perms:            # mentions user in ping channel to ping the fuck out of dev
                await self.ping_channel.send("{} you have an hour to ping the fuck out of dev".format(member.mention))

            await self.bot_testing_channel.send("Member perms will randomize again in an hour.")
            await asyncio.sleep(3600)

    @commands.command()
    @channel_check(config.bot_testing_channel)
    async def stoppermloop(self, ctx):
        self.loop_running = False
        await ctx.send("Perms for the spamming channel are no longer being looped, to resume, use the `!startpermloop` command")

    @commands.command()
    @channel_check(config.bot_testing_channel)
    async def removeperms(self, ctx):

        if len(self.members_with_perms) == 0:
            await ctx.send("There's already nobody with access to send messages to the channel")

        for member in self.ping_channel.members:
            if str(member.id) in self.ignored_members:
                pass
            elif self.ping_channel.overwrites_for(member).send_messages:
                await self.ping_channel.set_permissions(member, send_messages=None)
                await self.bot_testing_channel.send("{} can no longer send messages in ping channel".format(str(member)))

        await PingDev.update_members_with_perms(self)

    @commands.command()
    @channel_check(config.bot_testing_channel)
    async def checkperms(self, ctx):
        await PingDev.update_members_with_perms(self)
        if len(self.members_with_perms) == 0:
            await ctx.send("No members have permission to send messages in the channel")
            return

        clean_names = []
        for member in self.members_with_perms:
            clean_names.append(member.name)

        await ctx.send("Members with message send perms in the spam channel: {}".format(clean_names))



def setup(bot):
    bot.add_cog(PingDev(bot))
