from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from gigachat import GigaChat
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.fsm.context import FSMContext
import asyncio
import logging
import sys
import json
task_list = []
tag_list = []
done_task_list = []

with open('BOT_TOKEN.json') as file:
   new_data = json.load(file)

with open('GPT_TOKEN.json') as file_:
    data_ = json.load(file_)

GPT_TOKEN = data_['key']
TOKEN = new_data['key']
dp = Dispatcher()


class StateMachine(StatesGroup):
    explain_prompt = State()
    search_for_prompt = State()
    code_question_prompt = State()
    code_prompt = State()
    simplify_prompt = State()
    task_name = State()
    task_desc = State()
    task_level = State()
    task_deadline = State()
    task_tag = State()
    done_task_name = State()
    tag_tag1 = State()
    tag_tag2 = State()




class task():
    def __init__(self, name, description, deadline='none', level='none', tag='none', time=-1):
        self.name = name
        self.description = description
        self.tag = tag
        self.deadline = deadline
        self.level = level

    def delete_tag(self, delete_tag):
        if self.tag == delete_tag: self.tag = 'none'

def dictify(task):
    result = {
        "name": task.name,
        "description": task.description,
        "tag": task.tag,
        "deadline": task.deadline,
        "level": task.level
    }
    return result


def write_tasks(task_list_, done_task_list_, id):
    res_json = {}
    res_json['task_list'] = task_list_
    res_json['done_task_list'] = done_task_list_
    with open(f'Users/{id}.json', 'w') as outfile:
        json.dump(res_json, outfile)


def zadacha_done(name_zad):  # присваивает по названию задачи значение выполнения True
    for elem in task_list:
        if elem["name"] == name_zad:
            done_task_list.append(elem)
            task_list.pop(task_list.index(elem))


def zadacha_del(name_zad):  # удаляет задачу по ее названию
    for elem in task_list:
        if elem["name"] == name_zad:
             task_list.pop(task_list.index(elem))


def tag_task(tag, name_zad):  # добавление тега к задаче
    if tag in tag_list:
        for task in task_list:
            if task["name"] == name_zad: task["tag"] = tag


def delete_whole_tag(tag, keep_tasks):
    for elem in task_list:
        if elem["tag"] == tag:
            if keep_tasks is False:
                task_list.pop(task_list.index(elem))
            else:
                elem["tag"] = ""





def keyboard_start():
    builder = ReplyKeyboardBuilder()
    builder.button(text="ИИ помощник")
    builder.button(text="Планировщик задач")
    return builder.as_markup()


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


def keyboard_plan():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Добавить задачу"),
        types.KeyboardButton(text="Удалить теги")
    )
    builder.row(
        types.KeyboardButton(text="Список выполненных задач"),
        types.KeyboardButton(text="Выполнить задачу")
    )
    builder.row(
        types.KeyboardButton(text="Список всех задач")
    )
    builder.row(
        types.KeyboardButton(text="В начало")
    )
    return builder.as_markup()


def keyboard_skip():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Пропустить"))
    return builder.as_markup()


def keyboard_tags():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Удалить все задачи с тегом"),
                types.KeyboardButton(text="Удалить тег из всех задач"))
    builder.row(types.KeyboardButton(text="В начало"))
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






@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}", reply_markup=keyboard_start())


@dp.message(F.text.lower() == "ии помощник")
async def ai(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "планировщик задач")
async def plan_message(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_plan())


@dp.message(F.text.lower() == "добавить задачу")
async def add_task(message: Message, state):
    await state.set_state(StateMachine.task_name)
    await message.answer(f"Напишите название задачи")


@dp.message(StateMachine.task_name)
async def task_name(message: Message, state):
    await state.update_data(task_name=message.text)
    await state.set_state(StateMachine.task_desc)
    await message.answer(f"Напишите описание задачи")


@dp.message(StateMachine.task_desc)
async def task_desc(message: Message, state):
    await state.update_data(task_desc=message.text)
    await state.set_state(StateMachine.task_level)
    await message.answer(f"Напишите уровень сложности задачи (не обязательно)", reply_markup=keyboard_skip())


@dp.message(StateMachine.task_level)
async def task_level(message: Message, state):
    if(message.text.lower() != "пропустить"):
        await state.update_data(task_level=message.text)
        await state.set_state(StateMachine.task_deadline)
        await message.answer(f"Напишите крайний срок выполнения задачи (не обязательно)", reply_markup=keyboard_skip())
    else:
        await state.update_data(task_level="")
        await state.set_state(StateMachine.task_deadline)
        await message.answer(f"Напишите крайний срок выполнения задачи (не обязательно)", reply_markup=keyboard_skip())


@dp.message(StateMachine.task_deadline)
async def task_deadline(message: Message, state):
    if (message.text.lower() != "пропустить"):
        await state.update_data(task_deadline=message.text)
        await state.set_state(StateMachine.task_tag)
        await message.answer(f"Напишите тег задачи (не обязательно)", reply_markup=keyboard_skip())
    else:
        await state.update_data(task_deadline="")
        await state.set_state(StateMachine.task_tag)
        await message.answer(f"Напишите тег задачи (не обязательно)", reply_markup=keyboard_skip())


@dp.message(StateMachine.task_tag)
async def task_tag(message: Message, state):
    if (message.text.lower() != "пропустить"):
        await state.update_data(task_tag=message.text)
        data = await state.get_data()
        task_list.append(dictify(task(data["task_name"],
                                      data["task_desc"], data["task_deadline"], data["task_level"], data["task_tag"])))
        write_tasks(task_list, done_task_list, message.from_user.id)
        await message.answer("Задача успешно добавлена", reply_markup=keyboard_plan())
        await state.clear()
    else:
        await state.update_data(task_tag="")
        data = await state.get_data()
        task_list.append(dictify(task(data["task_name"],
                                      data["task_desc"], data["task_deadline"], data["task_level"], data["task_tag"])))
        write_tasks(task_list, done_task_list, message.from_user.id)
        await message.answer("Задача успешно добавлена", reply_markup=keyboard_plan())
        await state.clear()


@dp.message(F.text.lower() == "удалить теги")
async def delete_tags(message: Message):
    await message.answer(f"Как именно удалить теги", reply_markup=keyboard_tags())


@dp.message(F.text.lower() == "удалить все задачи с тегом")
async def delete_tags_and_tasks(message: Message, state):
    await message.answer(f"Введите тег", reply_markup=keyboard_plan())
    await state.set_state(StateMachine.tag_tag1)


@dp.message(StateMachine.tag_tag1)
async def del_tags_and_tasks_process(message: Message, state):
    await state.update_data(tag_tag1=message.text)
    data = await state.get_data()
    delete_whole_tag(data["tag_tag1"], False)
    write_tasks(task_list, done_task_list, message.from_user.id)
    await message.answer(f"Задачи с тегом {data['tag_tag1']} успешно удалены", reply_markup=keyboard_plan())
    await state.clear()


@dp.message(F.text.lower() == "удалить тег из всех задач")
async def delete_only_tag(message: Message, state):
    await message.answer(f"Введите тег", reply_markup=keyboard_plan())
    await state.set_state(StateMachine.tag_tag2)


@dp.message(StateMachine.tag_tag2)
async def delete_only_tag_process(message: Message, state):
    await state.update_data(tag_tag2=message.text)
    data = await state.get_data()
    delete_whole_tag(data['tag_tag2'], True)
    write_tasks(task_list, done_task_list, message.from_user.id)
    await message.answer(f"Тег {data['tag_tag2']} из задач успешно удален", reply_markup=keyboard_plan())
    await state.clear()


@dp.message(F.text.lower() == "список всех задач")
async def spisok_zad(message: Message):
    try:
        with open(f'Users/{message.from_user.id}.json') as file:
            file_data = json.load(file)
        show_task_list = file_data['task_list']
        for i in range(len(show_task_list)):
            rez = f"название:{show_task_list[i]['name']}\nописание:{show_task_list[i]['description']}"
            if show_task_list[i]["deadline"] != 'none': rez += '\nкрайний срок выполнения:' + show_task_list[i]["deadline"]
            if show_task_list[i]["level"] != 'none': rez += '\nуровень сложности:' + show_task_list[i]["level"]
            if show_task_list[i]["tag"] != 'none': rez += '\nтег:' + show_task_list[i]["tag"]
            await message.answer(rez, reply_markup=keyboard_plan())
    except FileNotFoundError:
        await message.answer("Записей ещё нету.", reply_markup=keyboard_plan())


@dp.message(F.text.lower() == "список выполненных задач")
async def spisok_done(message: Message):
    try:
        with open(f'Users/{message.from_user.id}.json') as file:
            done_file_data = json.load(file)
        show_done_task_list = done_file_data['done_task_list']
        for i in range(len(show_done_task_list)):
            rez = f"название:{show_done_task_list[i]['name']}\nописание:{show_done_task_list[i]['description']}"
            if show_done_task_list[i]["deadline"] != 'none': rez += '\nкрайний срок выполнения:' + show_done_task_list[i]["deadline"]
            if show_done_task_list[i]["level"] != 'none': rez += '\nуровень сложности:' + show_done_task_list[i]["level"]
            if show_done_task_list[i]["tag"] != 'none': rez += '\nтег:' + show_done_task_list[i]["tag"]
            await message.answer(rez, reply_markup=keyboard_plan())
    except FileNotFoundError:
        await message.answer("Записей ещё нету.", reply_markup=keyboard_plan())


@dp.message(F.text.lower() == "выполнить задачу")
async def spisok_done_1(message: Message, state):
    await state.set_state(StateMachine.done_task_name)
    await message.answer(f"Напишите название задачи")


@dp.message(StateMachine.done_task_name)
async def spisok_done_2(message: Message, state):
    await state.update_data(task_name=message.text)
    data = await state.get_data()
    zadacha_done(data["task_name"])
    write_tasks(task_list, done_task_list, message.from_user.id)
    await message.answer(f"Задача успешно выполнена", reply_markup=keyboard_plan())
    await state.clear()


@dp.message(F.text.lower() == "ии помощник")
async def ai(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "планировщик задач")
async def plan_message(message: types.Message):
    await message.reply(text="Чем Вам помочь?", reply_markup=keyboard_plan())


@dp.message(F.text.lower() == "объясни")
async def explain(message: types.Message, state: FSMContext):
    await state.set_state(StateMachine.explain_prompt)
    await message.answer(text="Скажи, какую тему тебе надо объяснить.", reply_markup=ReplyKeyboardRemove())

@dp.message(StateMachine.explain_prompt)
async def process_explain(message: types.Message, state: FSMContext):
    await state.update_data(explain_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот объяснение этой темы.")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False, model="GigaChat-Pro") as giga:
        response = giga.chat("Объясни мне вот эту тему: " + message.text)
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "подбери материалы")
async def search_for(message: types.Message, state: FSMContext):
    await state.set_state(StateMachine.search_for_prompt)
    await message.answer(text="Скажи, по какой теме надо подобрать материалы.", reply_markup=ReplyKeyboardRemove())


@dp.message(StateMachine.search_for_prompt)
async def process_search_for(message: types.Message, state: FSMContext):
    await state.update_data(search_for_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот материалы:")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False) as giga:
        response = giga.chat("Подбери мне 10 разных ссылок, в которых ОБЯЗАТЕЛЬНО рассказывается про эту тему: " + message.text + ". Оформи их в виде маркированного списка.")
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())


@dp.message(F.text.lower() == "ответь на вопрос по коду")
async def code(message: types.Message, state: FSMContext):
    await state.set_state(StateMachine.code_prompt)
    await message.answer(text="Отправь код.", reply_markup=ReplyKeyboardRemove())


@dp.message(StateMachine.code_prompt)
async def code_process(message: types.Message, state: FSMContext):
    await state.update_data(code_prompt=message.text)
    await state.set_state(StateMachine.code_question_prompt)
    await message.answer(text="Теперь скажи свой вопрос по коду.", reply_markup=ReplyKeyboardRemove())


@dp.message(StateMachine.code_question_prompt)
async def code_question_prompt(message: types.Message, state: FSMContext):
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
async def simplify(message: types.Message, state: FSMContext):
    await state.set_state(StateMachine.simplify_prompt)
    await message.answer(text="Отправь текст, который надо законспектировать.", reply_markup=ReplyKeyboardRemove())


@dp.message(F.text.lower() == "в начало")
async def to_start(message: types.Message):
    await message.answer(text="Возвращаю в начало!", reply_markup=keyboard_start())


@dp.message(StateMachine.simplify_prompt)
async def process_simplify(message: types.Message, state: FSMContext):
    await state.update_data(simplify_prompt=message.text)
    await state.set_state(None)
    await message.answer(text="Вот конспект:")
    with GigaChat(credentials=GPT_TOKEN, verify_ssl_certs=False) as giga:
        response = giga.chat("Кратко перескажи следующий текст: " + message.text)
        chatresponse = response.choices[0].message.content
        await message.answer(text=chatresponse, reply_markup=keyboard_ai())



async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
    print(task_list)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())