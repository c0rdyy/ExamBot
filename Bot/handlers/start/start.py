from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command

from config.settings import ADMIN_IDS
from keyboards.test import *
from keyboards.test_keyboard import *
from handlers.start.states import TestState
from database.requests import get_random_questions, save_test_result

start_router = Router()

@start_router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        keyboard = admin_main_menu_keyboard()
    else:
        keyboard = user_main_menu_keyboard()

    await message.answer("Добро пожаловать в главное меню! Выберите действие:", 
                         reply_markup=keyboard)

@start_router.callback_query(TestState.choosing_difficulty)
async def choose_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.replace("difficulty_", "")

    questions = await get_random_questions(difficulty)

    if len(questions) < 1:
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

        await save_test_result(message.from_user.id, score, rating_score, data["difficulty"])

        await message.answer(f"✅ Тест завершён!\n"
                             f"Правильных ответов: {correct} из {total}\n"
                             f"Оценка: {score}/5")
        await state.clear()
        return

    q = questions[index]
    options = q.options
    kb = build_question_keyboard(options)

    await message.answer(f"Вопрос {index+1}:\n{q.text}", reply_markup=kb)

    # 👇 Обязательное обновление состояния, чтобы handle_answer() работал
    await state.set_state(TestState.answering)


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
    await state.clear()
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

