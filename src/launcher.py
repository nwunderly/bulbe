import logging
from argparse import ArgumentParser

import uvicorn

from bulbe.bot import bot  # bulbe
from github.app import app  # fastapi app for github integration
from utils import auth
from utils.helpers import setup_logger

logger = logging.getLogger('bot.launcher')


def start_discord(args):
    prod = args.prod
    log = args.log

    if not log:
        log = 'info' if prod else 'debug'

    level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR,
    }[log]

    setup_logger("bot", level)
    setup_logger("cogs", level)
    setup_logger("utils", level)
    setup_logger('discord', logging.INFO)

    logger.info("Calling run method.")
    try:
        bot.run(auth[''])
    finally:
        try:
            exit_code = bot._exit_code
        except AttributeError:
            logger.info("Bot's exit code could not be retrieved.")
            exit_code = 0
        logger.info(f"Bot closed with exit code {exit_code}.")
        exit(exit_code)


def start_github(args):
    prod = args.prod
    log = args.log

    if not log:
        log = 'info' if prod else 'debug'

    level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR,
    }[log]

    setup_logger("bot", level)
    setup_logger("cogs", level)
    setup_logger("utils", level)
    setup_logger('discord', logging.INFO)

    uvicorn.run(app, host='0.0.0.0', port=9000)


def main():

    parser = ArgumentParser(description="Launch Bulbe Discord or GitHub bot.")
    subcommands = parser.add_subparsers()

    discord = subcommands.add_parser('discord')
    discord.add_argument('--log')
    discord.add_argument('--prod', action='store_true')
    discord.set_defaults(execute=start_discord)

    github = subcommands.add_parser('github')
    github.add_argument('--log')
    github.add_argument('--prod', action='store_true')
    github.set_defaults(execute=start_github)

    args = parser.parse_args()
    args.execute(args)


if __name__ == "__main__":
    main()
