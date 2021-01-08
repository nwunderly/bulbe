import discord
import aionasa


class Settings:
    version = '3.0.0'
    prefix = "++"

    embed_color = discord.Color(int('2ecc71', 16))

    logging_channel = 559509631466995749
    invite_permissions = 2110258423

    cogs = [
        'jishaku',
        # 'bulbe.cogs.admin',
        # 'bulbe.cogs.config',
        # 'bulbe.cogs.devtools',
        'bulbe.cogs.fun',
        # 'bulbe.cogs.manager',
        # 'bulbe.cogs.utilities',
    ]

    bot_perms = {
        'options': [
            'admin',      # all
            'root',       # eval, shell
            'manager',    # manage this bot (everything but eval/shell, permissions)
            'config',     # global config access
            'moderator',  # global server_admin permissions
        ],
        204414611578028034: [  # nwunder
            'admin'
        ]
    }

    activities = [
        'playing version '+version+"!",
        'playing #001 in the dex, #001 in the heart.',
        'playing with other bulbasaurs',
        'listening to bulbasaur sounds',
        'playing bulbe games',
        'watching pokemon',
        'playing pokemon',
        'watching for +help',
        'playing with +translate!',
        'playing epic bulbasaur moment',
        'playing smh my head',
        'playing ok, this is epic',
    ]
