import asyncio

from utils.translate import Translate


async def translate_text(text):
    print(await Translate().translate(text))


async def convert_language(name):
    print(await Translate().convert_lang(name))


async def main():
    await translate_text("bonjour")
    await convert_language("English")


asyncio.run(main())
