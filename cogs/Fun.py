import discord, random, asyncio, json
import requests

from config import settings
from discord.ext import commands

def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

def get_quotes():
    with open('config/phrases.json') as f:
        return json.load(f)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def selfdestruct(message):
        await asyncio.sleep(1)
        await message.channel.send("Initiating self destruct in 5...")
        await asyncio.sleep(1)
        await message.channel.send("4...")
        await asyncio.sleep(1)
        await message.channel.send("3...")
        await asyncio.sleep(1)
        await message.channel.send("2...")
        await asyncio.sleep(1)
        await message.channel.send("1...")
        await asyncio.sleep(1)
        await message.channel.send("Goodbye :-(")
        quit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions and not(message.content.startswith('!')):
            random_phrase = random.choice(get_quotes())
            await message.channel.send(random_phrase)
            # if random_phrase == "Nock is a GOD. Wait...":
            #     await Fun.selfdestruct(message) # sorry aly :( i dont want heroku to get mad
            return

        if ('counterclaim'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            counterclaim_phrases = []
            for phrase in get_quotes():
                if 'counterclaim'.casefold() in phrase.casefold():
                    counterclaim_phrases.append(phrase)
            await message.channel.send(random.choice(counterclaim_phrases))
            return

        if ('gone'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            await message.channel.send(':crab:')
            return

        if ('hi bot'.casefold() in message.content.casefold()) and not(message.content.startswith('!')):
            await message.channel.send('hi how are you')
            return

    @commands.command(aliases=['ss', 'share'])
    async def screenshare(self, ctx):
        member: discord.Member = ctx.author
        for channel in member.guild.channels:  # Loop through a list of channel objects in the guild
            if not isinstance(channel, discord.VoiceChannel):  # Current channel isn't a voice channel, check next one
                continue

            # We have a voice channel, check to see if our user is in the channel
            if member in channel.members:
                guild_id = member.guild.id  # Get the guild ID
                channel_id = channel.id  # Get the Channel ID
                await ctx.send(f"{member.mention} Here ya go!\nhttps://discordapp.com/channels/{guild_id}/{channel_id}")  # Send them the message!
                return

        # If we get to this point, our user isn't in a voice channel.
        await ctx.send(f"{member.mention} You aren't in a voice channel!")
        return

    @commands.command()
    @channel_check(settings.bot_managing_channel)
    async def ping(self, ctx):
        await ctx.send("Pong")

    @commands.command()
    async def aetball(self, ctx, input):
        random_phrase = random.choice(settings.aetball_list)
        await ctx.send(random_phrase)

    @commands.command()
    @channel_check(settings.bot_managing_channel)
    async def msg(self, ctx, channel_id: int, *, content):
        channel = self.bot.get_channel(channel_id)
        await channel.send(content)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send("I got {}.".format(random.choice(['heads', 'tails'])))

    @commands.command()
    async def rps(self, ctx, user_choice: str):
        valid_choices = ['rock', 'paper', 'scissors']

        if user_choice == 'Puits':
            await ctx.send("J\'ai choisi " + random.choice(valid_choices) + ", Tu as choisi le Puits\n**NOOON J\'AI PERDU PUTAIN**")
            return

        if user_choice == 'Turkey':
            await ctx.send("J\'ai choisi" + random.choice(valid_choices) + ", you picked Turkey.\n**I CAUGHT FUCKING DINNER!**")
            return

        if user_choice.lower() in valid_choices:
            bot_choice = random.choice(valid_choices)

            await ctx.send("Tu as choisi {}\nJ\'ai choisi {}".format(user_choice.lower(), bot_choice))

            if bot_choice == user_choice:
                await ctx.send("**Égalité!**")
            elif bot_choice == 'scissors' and user_choice == 'rock':
                await ctx.send("**Tu as gagné!**")
            elif bot_choice == 'paper' and user_choice == 'scissors':
                await ctx.send("**Tu as gagné!**")
            elif bot_choice == 'rock' and user_choice == 'paper':
                await ctx.send("**Tu as gagné!**")
            else:
                await ctx.send("**J\'ai gagné!**")
            return

        else:
            await ctx.send("Invalid choice, only accepted inputs are 'rock', 'paper', or 'scissors'.")
            return

    # @commands.command()
    # @channel_check(settings.bot_testing_channel)
    # async def die(self, ctx):
    #     await ctx.send("aw goodbye :(")
    #     quit()


def setup(bot):
    bot.add_cog(Fun(bot))
#FUCK
@register('serveravatar', rate=5)
async def serveravatar(message,*args):
    """Show the avatar for the current server"""
    server = message.server
    avatar = server_icon(server)
    embed = discord.Embed(title='Image for {server.name}'.format(server=server), color=colour(message.author))
    embed.set_image(url=avatar)

    await client.send_message(message.channel,embed=embed)


@register('r', 'in <<number of> [seconds|minutes|hours|days]|<on|at> <time>> "[message]"', alias='remindme')
@register('remindme', 'in <<number of> [seconds|minutes|hours|days]|<on|at> <time>> "[message]"')
async def remindme(message, *args):
    if len(args) < 3:
        return False

    word_units = {'couple': (2, 2), 'few': (2,4), 'some': (3, 5), 'many': (5, 15), 'lotsa': (10, 30)}

    if args[0] in ['in','on','at']:
        pass
    elif (not args[1] in word_units) or (not args[1].isnumeric()) or (int(args[1]) <= 0):
        return False

    invoke_time = int(time.time())

    logger.debug('Set reminder')
    await client.send_typing(message.channel)

    if args[0] == 'in':
        reminder_msg = ' '.join(args[2::])
        is_cancelled = False
        split = reminder_msg.split(' ',1)
        unit = split[0]
        unit_specified = True
        reminder_if_unit = split[1] if len(split) > 1 else None

        _s = ['seconds','second','sec','secs']
        _m = ['minutes','minute','min','mins']
        _h = ['hours'  ,'hour'  ,'hr' ,'hrs' ]
        _d = ['days'   ,'day'   ,'d'         ]

        if unit in _s:
            unit_mult = 1
        elif unit in _m:
            unit_mult = 60
        elif unit in _h:
            unit_mult = 3600
        elif unit in _d:
            unit_mult = 3600 * 24
        else:
            unit_mult = 60
            unit_specified = False

        if not reminder_if_unit and not unit_specified:
            return False

        if reminder_if_unit and unit_specified:
            reminder_msg = reminder_if_unit

        if not reminder_msg:
            return False

        if args[1] in word_units:
            args[1] = randrange(*word_units[args[1]])

        remind_delta = int(args[1]) * unit_mult
        remind_timestamp = invoke_time + remind_delta

    elif args[0] in ['at','on']:
        matches = re.findall(r'([^\"\']*) ([\"\'])(\2{0}[^\2]*)\2',' '.join(args))
        try:
            for match in matches:
                date_string,_,reminder_msg = match
                break

            parsed = parse(date_string)
        except:
            return False

        remind_timestamp = parsed.timestamp()
        remind_delta = int(remind_timestamp - datetime.now().timestamp())
        is_cancelled = False

    if remind_delta <= 0:
        msg = await client.send_message(message.channel, MESG.get('reminder_illegal','Illegal argument'))
        asyncio.ensure_future(message_timeout(msg, 20))
        return

    mentions = []
    if message.mentions:
        mentions = [member.id for member in message.mentions]

    reminder = {
        'invoke_time': invoke_time, 
        'channel_id': message.channel.id, 
        'user_id': message.author.id, 
        'user_name': message.author.display_name,
        'mentions': mentions,
        'message': reminder_msg, 
        'time': remind_timestamp, 
        'is_cancelled': is_cancelled,
        'task': None, 
    }

    reminders.append(reminder)
    async_task = asyncio.ensure_future(do_reminder(client, invoke_time))
    reminder['task'] = async_task

    logger.info(' -> reminder scheduled for ' + str(datetime.fromtimestamp(remind_timestamp)))
    msg = await client.send_message(message.channel, message.author.mention + ' Reminder scheduled for ' + datetime.fromtimestamp(remind_timestamp).strftime(CONF.get('date_format','%A %d %B %Y @ %I:%M%p')))
    asyncio.ensure_future(message_timeout(msg, 60))

    save_reminders()

@register('reminders','<username or all>',rate=1)
async def list_reminders(message,*args):
    logger.debug('Listing reminders')

    msg = 'Current reminders:\n'
    reminders_yes = ''


    def user_reminders(user,reminder):
        return reminder.get('user_id', '') == user.id

    all_users = False
    if not args:
        user = message.author
        filtered_reminders = filter(lambda r: user_reminders(user,r), reminders)
    elif args[0] == 'all':
        filtered_reminders = reminders
        all_users = True
    else:
        user = None
        if message.mentions: user = message.mentions[0]
        if not user: user = message.server.get_member_named(args[0])

        if not user:
            await client.send_message(message.channel,'User `{}` not found.'.format(args[0]))
            return

        filtered_reminders = filter(lambda r: user_reminders(user,r), reminders)

    for rem in filtered_reminders:
        try:
            if not message.server.get_channel(rem['channel_id']): continue
        except: continue

        try: date = datetime.fromtimestamp(rem['time']).strftime(CONF.get('date_format','%A %d %B %Y @ %I:%M%p'))
        except: date = str(rem['time'])

        if not rem.get('is_cancelled',False):
            now = datetime.now()
            try: t = datetime.fromtimestamp(rem['time'])
            except:
                t = datetime.now()
                logger.debug("bad date: {}".format(rem['time']))

            m = "{} remaining".format(time_diff(now,t))

            reminders_yes += ''.join([x for x in (rem.get('user_id', '') + ' at ' + date + ' ({})'.format(m) + ': ``' + rem.get('message', '') +'`` (id:`'+str(rem.get('invoke_time', ''))+'`)\n') if x in ALLOWED_EMBED_CHARS or x == '\n'])

    embed = discord.Embed(title="Reminders {}in {}".format(("for {} ".format(user.display_name)) if not all_users else '',message.server.name),color=colour(message.author),description='No reminders set' if len(reminders_yes) == 0 else discord.Embed.Empty)
    embed.set_footer(icon_url=server_icon(message.server),text='{:.16} | PedantBot Reminders'.format(message.server.name))
    if len(reminders_yes) > 0:
        embed.add_field(name='__Current Reminders__',value='{:.1000}'.format(reminders_yes))

    msg = await client.send_message(message.channel, embed=embed)
    asyncio.ensure_future(message_timeout(msg, 90))

@register('cancelreminder','<reminder id>')
async def cancel_reminder(message,*args):
    """Cancel an existing reminder"""
    global reminders
    if len(args) != 1:
        return

    logger.info('Cancel reminder')

    invoke_time = int(args[0])

    try:
        reminder = get_reminder(invoke_time)
        reminder['is_cancelled'] = True
        reminder['task'].cancel()
    except:
        msg = await client.send_message(message.channel,'Reminder not found.')
        asyncio.ensure_future(message_timeout(msg, 20))
        return

    msg = await client.send_message(message.channel,'Reminder #{0[invoke_time]}: `"{0[message]}"` removed.'.format(reminder))
    asyncio.ensure_future(message_timeout(msg, 20))
    reminders = [x for x in reminders if x['invoke_time'] != invoke_time]

@register('editreminder', '<reminder ID> <message|timestamp> [data]',rate=3)
async def edit_reminder(message,*args):
    """Edit scheduled reminders"""
    logger.info('Edit reminder')

    invoke_time = int(args[0])

    reminder = get_reminder(invoke_time)

    if not reminder:
        msg = await client.send_message(message.channel, 'Invalid reminder ID `{0}`'.format(invoke_time))
        asyncio.ensure_future(message_timeout(msg, 20))
        return

    try:
        if args[1].lower() in ['message','msg']:
            reminder['message'] = ' '.join(args[2::])

        elif args[1].lower() in ['timestamp','time','ts']:
            reminder['time'] = int(args[2])

        else:
            return False
    except:
        return False

    reminder['task'].cancel()
    async_task = asyncio.ensure_future(do_reminder(client, invoke_time))
    reminder['task'] = async_task

    msg = await client.send_message(message.channel, 'Reminder re-scheduled')
    asyncio.ensure_future(message_timeout(msg, 40))