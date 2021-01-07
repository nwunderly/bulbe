import asyncio
import datetime
import logging
import sys

logger = logging.getLogger('utils.helpers')


def list_by_category(guild):
    channels = []
    for category, category_channels in guild.by_category():
        if category is not None:
            channels.append(category)
        for channel in category_channels:
            channels.append(channel)
    return channels


def setup_logger(name, debug):
    _logger = logging.getLogger(name)
    d = datetime.datetime.now()
    time = f"{d.month}-{d.day}_{d.hour}h{d.minute}m"

    filename = '/logs/{}.log'
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    file_handler = logging.FileHandler(filename.format(time))
    # file_handler.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(stream_handler)
    _logger.setLevel(level)
    return _logger


async def try_run(coro):
    try:
        return await coro
    except:
        logger.exception(f"Encountered error in try_run:")
        return


async def maybe_coroutine(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


async def fetch_previous_message(message):
    use_next = False
    async for m in message.channel.history(limit=10):
        if use_next:
            return m
        if m.id == message.id:
            use_next = True
    return None