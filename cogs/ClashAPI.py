import aiohttp
from discord import Embed
from discord.ext import commands
from config import tasks
"""
District dictionaries have the following keys:

    'name': string, name of district
    'online': bool, true if district is online
    'population': int, population of the district
    'invasion_online': bool, true if its invaded
    'last_update': int, unix time for last update
    'cogs_attacking': string, name of the cog attacking
    'count_defeated': int, cogs defeated in the district
    'count_total': int, total cogs to invade the district
    'remaining_time': int, time til invasion ends in seconds

"""


class ClashAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def request(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status is 200:  # A request status code of 200 just means success
                    return r.status, await r.json()
                else:
                    return r.status, None

    @commands.command(aliases=['cc', 'ttcc', 'clash'])
    async def districts(self, ctx):

        request_status, unsorted_districts = await self.request('https://corporateclash.net/api/v1/districts.js')
        if request_status is not 200:
            await ctx.send(f'{ctx.author.mention} Failed to communicate with the TTCC API!')
            return


        districts = sorted(unsorted_districts, key=lambda k: k['name'])

        district_names = []
        populations = []
        invasions = []

        safe_districts = ['Geyser Gulch', 'Kazoo Kanyon', 'Jellybean Junction']

        for district in districts:
            name = district['name']
            players = district['population']
            is_invaded = district['invasion_online']

            district_names.append(name)
            populations.append(players)

            if name in safe_districts:
                invasions.append('Safe District!')
                continue

            if is_invaded:
                cog = district['cogs_attacking']
                if cog == 'None':  # Not sure why but API sometimes reports 'None' as invaded cog :/
                    cog = 'Unknown'
                time_left = int(district['remaining_time'] / 60)
                # invasions.append(f'**{cog}** invasion for **{time_left} min!**')
                invasions.append(f'**Invaded for {time_left} min**')
            else:
                invasions.append('No invasion')


        embed_msg = Embed(
            title='\u200b',
            type='rich',
            description="",
            colour=0x7b75f0,  # Light blueish
        )

        district_names_string = '\n'.join(district_names)
        populations_string = '\n'.join([str(num) for num in populations])
        invasions_string = '\n'.join(invasions)

        total_population = sum(populations)

        embed_msg.set_author(name="Corporate Clash Info", icon_url='https://corporateclash.net/resources/img/logo_icon.png')

        embed_msg.add_field(name='Districts', value=district_names_string, inline=True)
        embed_msg.add_field(name='Population', value=populations_string, inline=True)
        embed_msg.add_field(name='Invasion Status', value=invasions_string, inline=True)

        embed_msg.add_field(name="\u200b", value="\u200b", inline=False)

        embed_msg.add_field(name=f'The Corporate Clash population is currently **{total_population}**', value="\u200b", inline=False)


        await ctx.send(embed=embed_msg)
   
   
    @commands.command(aliases=['task', 'tasks'])
    async def taskline(self, ctx, *, arg=None):

        if arg is None:

            await ctx.send(f"{ctx.author.mention} Here ya go! https://docs.google.com/document/d/1o5KcaS4xo1CdyBcqJOJ2o1j38oVWuEtXFqc-4aOOfZU/edit#")
            return

        if arg in tasks.lookup.keys():

            task_to_send = tasks.lookup[arg]
            await ctx.send(task_to_send)
        else:
            await ctx.send("Taskline is spelled incorrectly or does not exist.")

def setup(bot):
    bot.add_cog(ClashAPI(bot))
