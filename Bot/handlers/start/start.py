from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from keyboards.help_keyboard import help_back_keyboard
from keyboards.test import *
from keyboards.test_keyboard import *
from handlers.start.states import TestState
from database.requests import (
    get_random_questions,
    save_test_result,
    get_or_create_user,
    get_user_rank,
    get_user_by_id,
    get_top_users,
    update_user_photo)

start_router = Router()

@start_router.message(F.text == "/start")
async def cmd_start(message: Message):
    photo = FSInputFile("images/Main_menu.png")
    text = "👋 Добро пожаловать в главное меню!"

    user = await get_or_create_user(
        user_id=message.from_user.id,
        name=message.from_user.full_name
    )

    if user.is_admin:
        keyboard = admin_main_menu_keyboard()
    else:
        keyboard = user_main_menu_keyboard()

    await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)

@start_router.callback_query(TestState.choosing_difficulty)
async def choose_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.replace("difficulty_", "")
    questions = await get_random_questions(difficulty)

    if not questions:
        await callback.message.edit_caption("❌ Недостаточно вопросов для этого уровня.")
        await state.clear()
        return

    await state.update_data(questions=questions, index=0, correct=0, difficulty=difficulty)
    await ask_next_question(callback, state)


async def ask_next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data["index"]
    questions = data["questions"]
    msg_id = data["test_msg_id"]

    if index >= len(questions):
        total = len(questions)
        correct = data["correct"]
        percent = correct / total * 100

        score = (
            5 if percent >= 90 else
            4 if percent >= 70 else
            3 if percent >= 50 else
            2 if percent >= 30 else 1
        )

        weight = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
        rating_score = score * weight[data["difficulty"]]

        await save_test_result(callback.from_user.id, score, rating_score, data["difficulty"])

        rank = await get_user_rank(callback.from_user.id)

        result_text = (
            f"✅ <b>Тест завершён!</b>\n"
            f"🎯 Правильных ответов: {correct} из {total}\n"
            f"📊 Оценка: <b>{score}/5</b>\n"
            f"🏆 Место в рейтинге: <b>#{rank}</b>"
        )

        photo = FSInputFile("images/test/test_results.jpg")

        await callback.bot.edit_message_media(
            media=InputMediaPhoto(
                media=photo,
                caption=result_text,
                parse_mode="HTML"
            ),
            chat_id=callback.message.chat.id,
            message_id=msg_id,
            reply_markup=test_results_keyboard
        )

        await state.update_data(
            test_result_text=result_text,
            correct_answers=correct,
            total_questions=total,
            score=score,
            test_msg_id=msg_id
        )

        return

    q = questions[index]
    options = q.options
    question_text = f"❓ <b>Вопрос {index + 1}</b>\n\n{q.text}\n\n"
    question_text += "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(options)])

    kb = build_number_keyboard(len(options))

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=msg_id,
        caption=question_text,
        reply_markup=kb,
        parse_mode="HTML"
    )

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
    await ask_next_question(callback, state)

@start_router.callback_query(F.data == "back_to_main_menu")
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    user = await get_user_by_id(callback.from_user.id)

    if user.is_admin:
        keyboard = admin_main_menu_keyboard()
    else:
        keyboard = user_main_menu_keyboard()

    photo = FSInputFile("images/Main_menu.png")
    text = "👋 Вы вернулись в главное меню!"

    await callback.message.answer_photo(
        caption=text,
        photo=photo,
        reply_markup=keyboard
    )

@start_router.callback_query(F.data == "view_rating")
async def handle_view_rating(callback: CallbackQuery):
    await callback.answer()

    users = await get_top_users()
    text = "🏆 <b>Рейтинг пользователей</b>\n\n"
    for i, user in enumerate(users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        name = user.name or "—"
        text += f"{medal} <b>{name}</b> — <code>{user.total_score}</code>\n"

    photo = FSInputFile("images/rating.jpg")

    await callback.bot.edit_message_media(
        media=InputMediaPhoto(
            media=photo,
            caption=text,
            parse_mode="HTML"
        ),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=back_to_test_result_keyboard
    )

@start_router.callback_query(F.data == "back_to_test_result")
async def handle_back_to_test_result(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()

    correct = data.get("correct_answers", 0)
    total = data.get("total_questions", 1)
    score = data.get("score", 0)
    msg_id = data.get("test_msg_id")
    rank = await get_user_rank(callback.from_user.id)

    text = (
        f"✅ <b>Тест завершён!</b>\n\n"
        f"📈 Правильных ответов: {correct} из {total}\n"
        f"💯 Оценка: {score}\n"
        f"🏆 Ваше место в рейтинге: {rank}"
    )

    photo = FSInputFile("images/test/test_results.jpg")

    await callback.bot.edit_message_media(
        media=InputMediaPhoto(
            media=photo,
            caption=text,
            parse_mode="HTML"
        ),
        chat_id=callback.message.chat.id,
        message_id=msg_id,
        reply_markup=test_results_keyboard
    )


@start_router.message(F.text == "/test")
@start_router.message(F.text == "🧠 Начать тест")
async def handle_test(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()

    photo = FSInputFile("images/test/start_test.jpg")
    msg = await message.answer_photo(
        photo=photo, 
        caption="Выберите уровень сложности:",
        reply_markup=test_keyboard)

    await state.update_data(test_msg_id=msg.message_id)
    await state.set_state(TestState.choosing_difficulty)


@start_router.message(F.text == "/rate")
@start_router.message(F.text == "🏆 Рейтинг")
async def handle_rating(message: Message):
    await message.delete()

    users = await get_top_users()
    text = "🏆 <b>Рейтинг пользователей</b>\n\n"
    for i, user in enumerate(users, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        name = user.name or "—"
        text += f"{medal} <b>{name}</b> — <code>{user.total_score}</code>\n"

    photo = FSInputFile("images/rating.jpg")

    await message.answer_photo(
        photo=photo,
        caption=text,
        parse_mode="HTML",
        reply_markup=help_back_keyboard 
    )



@start_router.message(F.text == "/help")
@start_router.message(F.text == "❓ Помощь")
async def handle_help(message: Message):
    await message.delete()
    photo = FSInputFile("images/help.jpg")
    caption = (
        "ℹ️ <b>О боте:</b>\n"
        "Этот бот предназначен для прохождения тестов по объектно-ориентированному программированию (ООП).\n\n"
        "📌 <b>Команды и кнопки:</b>\n"
        "/start - запустить бота.\n"
        "/test — начать тест.\n"
        "/profile — открыть профиль.\n"
        "/rate — посмотреть свой рейтинг среди других пользователей.\n"
        "/help — показать справку по командам.\n\n"
    )
    
    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=help_back_keyboard
    )

