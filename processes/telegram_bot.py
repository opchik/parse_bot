import asyncio
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from db import BotDB


bot_db = BotDB()

class Menu(StatesGroup):
    difficulty = State()
    topic = State()
    topic_unique = State()
    merge_topic = State()
    merge_difficulty = State()

router = Router()



# start
@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    await bot_db.create_pool()
    await message.answer("Привет! Здесь ты можешь найти большое количество задач с codeforces.")



# Выбор команды из меню
@router.message(Command(commands=["difficulty","topic", "merge", "topic_unique"]))
async def switch_command(message: types.Message, state: FSMContext):
    if message.text == "/difficulty":
        await message.answer("Введите сложность (целое число от 800 до 3500).\nМожно вводить только числа кратные 100: 800, 900, 1000 и т.д.")
        await state.set_state(Menu.difficulty)

    elif message.text == "/topic":
        await message.answer("Введите тему")
        await state.set_state(Menu.topic)

    elif message.text == "/topic_unique":
        await message.answer("Введите тему")
        await state.set_state(Menu.topic_unique)

    elif message.text == "/merge":
        await message.answer("Введите тему")
        await state.set_state(Menu.merge_topic)



# сложность
@router.message(Menu.difficulty)
async def difficulty(message: types.Message, state: FSMContext):
    number = message.text
    if number.isdigit() and 800 <= int(number) <= 3500 and int(number) % 100 == 0:
        answer = await bot_db.get_problem(difficulty=number)
        if not answer:
            await message.answer("Произошла ошибка, повторите запрос")
        else:
            await message.answer(answer)
        await state.clear()
    else:
        await message.answer("Неправильный формат, повторите запрос")
        await state.set_state(Menu.difficulty)




# тема
@router.message(Menu.topic)
async def topic(message: types.Message, state: FSMContext):
    answer = await bot_db.get_problem(topic=message.text)
    if not answer:
        await message.answer("Произошла ошибка, повторите запрос")
    else:
        await message.answer(answer)
    await state.clear()



# уникальная тема 
@router.message(Menu.topic_unique)
async def topic(message: types.Message, state: FSMContext):
    answer = await bot_db.get_problem(topic_unique=message.text)
    if not answer:
        await message.answer("Произошла ошибка, повторите запрос")
    else:
        await message.answer(answer)
    await state.clear()



# все вместе
@router.message(Menu.merge_topic)
async def merge_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic_unique=message.text)
    await message.answer("Введите сложность (целое число от 800 до 3500).\nМожно вводить только числа кратные 100: 800, 900, 1000 и т.д.")
    await state.set_state(Menu.merge_difficulty)


@router.message(Menu.merge_difficulty)
async def merge_difficulty(message: types.Message, state: FSMContext):
    number = message.text
    if number.isdigit() and 800 <= int(number) <= 3500 and int(number) % 100 == 0:
        data = await state.get_data()
        answer = await bot_db.get_problem(topic_unique=data['topic_unique'], difficulty=number)
        if not answer:
            await message.answer("Произошла ошибка, повторите запрос. Возможно такой задачи не существует")
        else:
            await message.answer(answer)
        await state.clear()
    else:
        await message.answer("Неправильный формат, повторите запрос")
        await state.set_state(Menu.merge_difficulty)





@router.message()
async def all_mess(message: types.Message):
    await message.answer("Сообщение непонятно, воспользуйтесь командой.")

  
    