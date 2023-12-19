import asyncio
import logging
import socket

from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
import asyncpg

from core.handlers.basic import *
from core.middlewares.countermiddleware import CounterMiddleware
from core.middlewares.dbmiddleware import DbSession
from core.utils.commands import set_commands
from env import db_host, bot_token, user_id_for_push, db_name, db_user, db_pass

async def create_pool():
    return await asyncpg.create_pool(host=db_host, port=5432, database=db_name, user=db_user, password=db_pass, command_timeout=60)

async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(user_id_for_push, text=f'<tg-spoiler>{socket.gethostname()}</tg-spoiler> запустил бота')

async def stop_bot(bot: Bot):
    await bot.send_message(user_id_for_push, text=f'<tg-spoiler>{socket.gethostname()}</tg-spoiler> отключил бота')

async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )

    bot = Bot(bot_token, parse_mode='HTML')
    dp = Dispatcher()

    pool_connect = await create_pool()

    dp.update.middleware.register(DbSession(pool_connect))
    dp.message.middleware.register(CounterMiddleware())

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(get_cancel,Command(commands=['cancel']))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(start())