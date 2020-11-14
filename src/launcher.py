import yaml
import logging
from argparse import ArgumentParser

from bulbe import bot   # bulbe
from github import app  # fastapi app for github integration

from utils import checks
from utils import auth
from utils.utility import setup_logger, module_logger, HOME_DIR



def start_discord(args):
    prod = args.prod
    log = args.log

    if not log:
        log = 'info' if 'prod' else 'debug'

    level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR,
    }[log]

    logger = module_logger(name, "launcher", level)
    module_logger(name, 'discord', logging.INFO)

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
    debug = args.debug
    log = args.log


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
