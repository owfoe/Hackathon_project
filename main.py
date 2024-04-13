from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram import F
import asyncio
import json

import logging
import sys

with open('BOT_TOKEN.json') as file:
    data = json.load(file)

TOKEN = data['key']

dp = Dispatcher()

def keyboard_start():
    builder = ReplyKeyboardBuilder()
    builder.button(text="ИИ помощник")
    builder.button(text="Планировщик задач")
    return builder.as_markup()
def keyboard_ai():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Объясни")
    builder.button(text="Подбери материалы")
    builder.button(text="Ответь на вопрос по коду")
    builder.button(text="Сделай конспект")
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}", reply_markup=keyboard_start())

@dp.message(F.text.lower() == "ии помощник")
async def without_puree(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_ai())


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
    print("test")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())