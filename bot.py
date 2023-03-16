import asyncio
import time
from aiogram import Bot
from aiogram import Dispatcher
from processes import parser, telegram_bot
from db import BotDB
from multiprocessing import Process
import configparser 


config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['BOTDATA']['BOT_TOKEN']
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main(bot_db):
    dp.include_router(telegram_bot.router)
    await dp.start_polling(bot)


def bot_polling():
    while True:
        try:
            asyncio.run(main(bot_db))
            
        except Exception as e:
            logging.error(e)
            bot.stop_polling()
            time.sleep(5)
            logging.info("Running again!")


if __name__ == "__main__":
    bot_db = BotDB()
    asyncio.run(bot_db.create_db())
    p1 = Process(target=bot_polling)
    p2 = Process(target=parser.process_parse)
    p1.start()
    p2.start()

