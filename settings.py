from os import environ


SESSION_CONFIGS = [
    {
        'name': 'Stage_Control',
        'app_sequence': ['Stage_Control'],
        'num_demo_participants': 2,
        'display_name': "對照組",
    },

    {
        'name': 'Stage_CarbonTax',
        'app_sequence': ['Stage_CarbonTax'],
        'num_demo_participants': 2,
        'display_name': "碳稅組",
    },

    {
        'name': 'Stage_MUDA',
        'app_sequence': ['Stage_MUDA'],
        'num_demo_participants': 2,
        'display_name': "MUDA",
    },

    {
        'name': 'Stage_CarbonTrading',
        'app_sequence': ['Stage_CarbonTrading'],
        'num_demo_participants': 2,
        'display_name': "碳交易組",
    },

]


SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'TWD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5406477812875'

INSTALLED_APPS = ['otree']
