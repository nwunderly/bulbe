import logging
from argparse import ArgumentParser

import uvicorn

from bulbe.bot import Bulbe  # bulbe
# from github.app import app  # fastapi app for github integration
from utils.helpers import setup_logger
from auth import TOKEN_DEV, TOKEN_PROD, DB_URL_DEV, DB_URL_PROD


logger = logging.getLogger('bot.launcher')


log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'error': logging.ERROR,
}


def start_discord(args):
    dev = args.dev
    log = args.log

    if not log:
        log = 'debug' if dev else 'info'

    level = log_levels[log]

    setup_logger("bot", level)
    setup_logger("cogs", level)
    setup_logger("utils", level)
    setup_logger('discord', logging.INFO)

    token = TOKEN_DEV if dev else TOKEN_PROD
    db_url = DB_URL_DEV if dev else DB_URL_PROD
    bot = Bulbe(token, db_url)

    logger.info("Starting up.")

    try:
        bot.run()
    finally:
        try:
            exit_code = bot._exit_code
        except AttributeError:
            logger.info("Bot's exit code could not be retrieved.")
            exit_code = 0
        logger.info(f"Bot closed with exit code {exit_code}.")
        exit(exit_code)


# def start_github(args):
#     dev = args.dev
#     log = args.log
#
#     if not log:
#         log = 'debug' if dev else 'info'
#
#     level = log_levels[log]
#
#     setup_logger("github", level)
#     setup_logger("utils", level)
#
#     uvicorn.run(app, host='0.0.0.0', port=9000)


def main():

    parser = ArgumentParser(description="Launch Bulbe Discord or GitHub bot.")
    subcommands = parser.add_subparsers()

    discord = subcommands.add_parser('discord')
    discord.add_argument('--log')
    discord.add_argument('--dev', action='store_true')
    discord.set_defaults(execute=start_discord)

    # github = subcommands.add_parser('github')
    # github.add_argument('--log')
    # github.add_argument('--dev', action='store_true')
    # github.set_defaults(execute=start_github)

    args = parser.parse_args()
    args.execute(args)


if __name__ == "__main__":
    main()
