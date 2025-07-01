from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command

from sqlalchemy import select
from database.models import async_session, Question

from sqlalchemy.sql import func

from config.admin_ids import ADMIN_IDS
from keyboards.test import *
from keyboards.test_keyboard import *
from database.states import TestState

start_router = Router()

@start_router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        keyboard = admin_main_menu_keyboard()
    else:
        keyboard = user_main_menu_keyboard()

    await message.answer("Добро пожаловать в главное меню! Выберите действие:", reply_markup=keyboard)

@start_router.callback_query(TestState.choosing_difficulty)
async def choose_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.replace("difficulty_", "")
    async with async_session() as session:
        result = await session.execute(
            select(Question).where(Question.difficulty == difficulty).order_by(func.random()).limit(10)
        )
        questions = result.scalars().all()

    if len(questions) < 10:
        await callback.message.answer("Недостаточно вопросов для этого уровня.")
        await state.clear()
        return

    await state.update_data(questions=questions, index=0, correct=0, difficulty=difficulty)
    await callback.message.delete()
    await ask_next_question(callback.message, state)

async def ask_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data["index"]
    questions = data["questions"]

    if index >= len(questions):
        # Завершить тест
        total = len(questions)
        correct = data["correct"]
        percent = correct / total * 100

        if percent >= 90:
            score = 5
        elif percent >= 70:
            score = 4
        elif percent >= 50:
            score = 3
        elif percent >= 30:
            score = 2
        else:
            score = 1

        # Балл в рейтинг с весом сложности
        weight = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
        rating_score = score * weight[data["difficulty"]]

        # Сохраняем результат в БД
        from models import Result
        async with async_session() as session:
            session.add(Result(
                user_id=message.from_user.id,
                score=score,
                rating_score=rating_score,
                difficulty=data["difficulty"]
            ))
            await session.commit()

        await message.answer(f"✅ Тест завершён!\n"
                             f"Правильных ответов: {correct} из {total}\n"
                             f"Оценка: {score}/5")
        await state.clear()
        return

    q = questions[index]
    options = q.options
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"answer_{i}")]
        for i, opt in enumerate(options)
    ])

    await message.answer(f"Вопрос {index+1}:\n{q.text}", reply_markup=kb)

@start_router.callback_query(F.data.startswith("answer_"), TestState.answering)
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data["index"]
    questions = data["questions"]
    q = questions[index]

    answer_index = int(callback.data.replace("answer_", ""))
    correct = data["correct"]
    if answer_index == q.correct_index:
        correct += 1

    await state.update_data(index=index + 1, correct=correct)
    await callback.message.delete()
    await ask_next_question(callback.message, state)

@start_router.message(F.text == "/test")
@start_router.message(F.text == "🧠 Начать тест")
async def handle_test(message: Message, state: FSMContext):
    await message.answer("Выберите уровень сложности:", reply_markup=test_keyboard)
    await state.set_state(TestState.choosing_difficulty)

@start_router.message(F.text == "/profile")
@start_router.message(F.text == "👤 Профиль")
async def handle_profile(message: Message):
    await message.answer("Ваш профиль:")

@start_router.message(F.text == "/rate")
@start_router.message(F.text == "🏆 Рейтинг")
async def handle_rating(message: Message):
    await message.answer("Текущий рейтинг:")

@start_router.message(F.text == "🛠 Админ-панель")
async def handle_admin(message: Message):
    await message.answer("Панель администратора:")

@start_router.message(F.text == "/help")
@start_router.message(F.text == "❓ Помощь")
async def handle_help(message: Message):
    help_text = (
        "ℹ️ *О боте:*\n"
        "Этот бот предназначен для прохождения тестов по объектно-ориентированному программированию (ООП).\n\n"
        "📌 *Команды и кнопки:*\n"
        "/start - запустить бота.\n"
        "/test — начать тест.\n"
        "/profile — открыть профиль.\n"
        "/rate — посмотреть свой рейтинг среди других пользователей.\n"
        "/help — показать справку по командам.\n\n"
    )
    await message.answer(help_text, parse_mode="Markdown")

