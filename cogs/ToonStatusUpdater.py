import discord, asyncio, toon

from config import settings
from discord.ext import commands

class ToonStatusUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_exists = False

    async def update_loop(self):
        await self.bot.wait_until_ready()


        for channel_id in settings.toon_status_channels: # Loop through all channels set to show toon statuses
            await self.bot.get_channel(channel_id).purge(limit=1) # Delete the old status message

        self.message_exists = True

        while True:
            try:
                await toon.update_embed(self.bot) # Initialize/update the status messages every 60 sec
            except:
                print("(ERROR) ToonStatusUpdater.update_embed() failed, trying again in a minute")

            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.message_exists:
            self.update_task = self.bot.loop.create_task(ToonStatusUpdater.update_loop(self))

def setup(bot):
    bot.add_cog(ToonStatusUpdater(bot))
