import aiogram.fsm.state
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram import F
from gigachat import GigaChat
import asyncio
import json

import logging
import sys

with open('BOT_TOKEN.json') as file:
    data = json.load(file)

with open('GPT_TOKEN.json') as file_:
    data_ = json.load(file_)

BOT_TOKEN = data['key']
GPT_TOKEN = data_['key']

dp = Dispatcher()

class StateMachine(aiogram.fsm.state.StatesGroup):
    explain_prompt = aiogram.fsm.state.State()
    search_for_prompt = aiogram.fsm.state.State()

    code_question_prompt = aiogram.fsm.state.State()
    code_prompt = aiogram.fsm.state.State()

    simplify_prompt = aiogram.fsm.state.State()


def keyboard_start():
    builder = ReplyKeyboardBuilder()
    builder.button(text="ИИ помощник")
    builder.button(text="Планировщик задач")
    return builder.as_markup()


def keyboard_tags():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Удалить все задачи с тегом")
    builder.button(text="Удалить тег из всех задач")


def keyboard_plan():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Добавить задачу")
    )
    builder.row(
        types.KeyboardButton(text="Удалить теги"),
        types.KeyboardButton(text="Изменить задачу")
    )
    builder.row(
        types.KeyboardButton(text="Список всех задач"),
        types.KeyboardButton(text="Выполнить задачу")
    )
    builder.row(
        types.KeyboardButton(text="Список выполненных задач"),
        types.KeyboardButton(text="Вывести статистику по задачам")
    )
    builder.row(
        types.KeyboardButton(text="В начало")
    )
    return builder.as_markup()

def keyboard_edit_task():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Изменить название"),
        types.KeyboardButton(text="Изменить тег"),
        types.KeyboardButton(text="Изменить описание"),
        types.KeyboardButton(text="Изменить крайний срок выполнения"),
        types.KeyboardButton(text="Изменить сложность"),
        types.KeyboardButton(text="Изменить частоту напоминаний")
    )
    builder.row(
        types.KeyboardButton(text="В начало")
    )


def keyboard_ai():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Объясни"),
        types.KeyboardButton(text="Подбери материалы"),
        types.KeyboardButton(text="Ответь на вопрос по коду"),
        types.KeyboardButton(text="Сделай конспект")
    )
    builder.row(
        types.KeyboardButton(text="В начало")
    )
    return builder.as_markup()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}", reply_markup=keyboard_start())


@dp.message(F.text.lower() == "ии помощник")
async def ai(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "планировщик задач")
async def plan_message(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_plan())


@dp.message(F.text.lower() == "объясни")
async def explain(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.set_state(StateMachine.explain_prompt)
    await message.answer(text="Скажи, какую тему тебе надо объяснить.", reply_markup=aiogram.types.ReplyKeyboardRemove())

@dp.message(StateMachine.explain_prompt)
async def process_explain(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.update_data(explain_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот объяснение этой темы.")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False, model="GigaChat-Pro") as giga:
        response = giga.chat("Объясни мне вот эту тему: " + message.text)
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "подбери материалы")
async def search_for(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.set_state(StateMachine.search_for_prompt)
    await message.answer(text="Скажи, по какой теме надо подобрать материалы.", reply_markup=aiogram.types.ReplyKeyboardRemove())


@dp.message(StateMachine.search_for_prompt)
async def process_search_for(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.update_data(search_for_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот материалы:")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False) as giga:
        response = giga.chat("Подбери мне 10 разных ссылок, в которых ОБЯЗАТЕЛЬНО рассказывается про эту тему: " + message.text + ". Оформи их в виде маркированного списка.")
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "ответь на вопрос по коду")
async def code(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.set_state(StateMachine.code_prompt)
    await message.answer(text="Отправь код.", reply_markup=aiogram.types.ReplyKeyboardRemove())


@dp.message(StateMachine.code_prompt)
async def code_process(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.update_data(code_prompt=message.text)
    await state.set_state(StateMachine.code_question_prompt)
    await message.answer(text="Теперь скажи свой вопрос по коду.", reply_markup=aiogram.types.ReplyKeyboardRemove())


@dp.message(StateMachine.code_question_prompt)
async def code_question_prompt(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.update_data(code_question_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот тебе ответ:")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False) as giga:
        data = await state.get_data()
        print(data['code_prompt'])
        response = giga.chat("Ответь на вопрос по коду. Вот код:" + data['code_prompt'] + "Вот вопрос:" + data['code_question_prompt'])
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "сделай конспект")
async def simplify(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.set_state(StateMachine.simplify_prompt)
    await message.answer(text="Отправь текст, который надо законспектировать.", reply_markup=aiogram.types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == "в начало")
async def to_start(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await message.answer(text="Возвращаю в начало!", reply_markup=keyboard_start())


@dp.message(StateMachine.simplify_prompt)
async def process_simplify(message: types.Message, state: aiogram.fsm.context.FSMContext):
    await state.update_data(simplify_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот конспект:")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False) as giga:
        response = giga.chat("Кратко перескажи следующий текст: " + message.text)
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())



async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
    print("test")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())