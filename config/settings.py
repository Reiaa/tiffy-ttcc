# This is the channel used for managing the bot, mostly used for Quote system
bot_managing_channel = 557395184577544222

# This list is used for updating toon statuses
toon_status_channels = [582752374360244228, 566229150407458848]

required_json_files = ['config/phrases.json', 'config/toon_nicknames.json', 'config/toons.json', 'config/valid_claiming_channels.json']

aetball_list = [
    'Very likely... bitch',
    'Of course not. That\'s cute though',
    'Yes sweetie',
    'Keep trying, it\'s fucking adorable',
	'Mmmmmmmmm',
    'Don\'t fucking count on it',
    'Of course not. That\'s so cute though',
    'Extremely doubtful',
    'No. Do not even fucking bother',
    'Yea',
    'Of course',
    'My encyclopedias say yes',
    'Signal. says yes',
    'Omg yes',
    'For sure',
    'Without a doubt',
    '100% yea',
    'You may rely on it',
    'Mmmm I\'m certain it\'s true',
    'Fuck off, I\'m busy fingering myself rn',
    'Ask again later sweetie',
    'I don\'t have an answer atm',
    'Try turning me on and off again',
    'Shut up I don\'t have time to listen to you',
    'Ask your father',
    'Ask your mother',
    'Ask <@334282153204514816> I\'m just her mere slave'
]

#ttcc gag damages

combo_bonuses = [0, 20, 20, 20]
drop_combo_bonuses = [0, 30, 40, 50]

TRAP = 0
LURE = 1
SOUND = 2
SQUIRT = 3
ZAP = 4
THROW = 5
DROP = 6

all_gags = {

    'banana_peel': (20, TRAP),
    'rake': (30, TRAP),
    'spring': (45, TRAP),
    'marbles': (60, TRAP),
    'quicksand': (85, TRAP),
    'trap_door': (140, TRAP),
    'wrecking_ball': (200, TRAP),
    'tnt': (240, TRAP),

    'lure': (0, LURE),

    'bike_horn': (4, SOUND),
    'whistle': (7, SOUND),
    'kazoo': (11, SOUND),
    'bugle': (16, SOUND),
    'aoogah': (21, SOUND),
    'trunk': (32, SOUND),
    'fog': (50, SOUND),
    'opera': (65, SOUND),

    'squirting_flower': (4, SQUIRT),
    'glass_of_water': (8, SQUIRT),
    'squirt_gun': (12, SQUIRT),
    'water_balloon': (21, SQUIRT),
    'seltzer_bottle': (30, SQUIRT),
    'fire_hose': (56, SQUIRT),
    'storm_cloud': (80, SQUIRT),
    'geyser': (115, SQUIRT),

    'joy_buzzer': (3, ZAP),
    'carpet': (6, ZAP),
    'balloon': (10, ZAP),
    'kart_battery': (16, ZAP),
    'taser': (24, ZAP),
    'tv': (40, ZAP),
    'tesla': (66, ZAP),
    'lightning': (80, ZAP),

    'cupcake': (7, THROW),
    'fruit_slice': (12, THROW),
    'cream_slice': (18, THROW),
    'cake_slice': (30, THROW),
    'fruit': (45, THROW),
    'cream': (75, THROW),
    'cake': (110, THROW),
    'wedding': (145, THROW),

    'flower_pot': (12, DROP),
    'sandbag': (20, DROP),
    'bowling_ball': (35, DROP),
    'anvil': (50, DROP),
    'big_weight': (70, DROP),
    'safe': (120, DROP),
    'boulder': (180, DROP),
    'piano': (220, DROP)

}
