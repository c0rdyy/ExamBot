from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.admin_panel.admin_panel_states import AddQuestionState, AdminPanelState
from keyboards.admin_panel_keyboard import *
from keyboards.test import user_main_menu_keyboard, admin_main_menu_keyboard
from database.requests import add_question, get_all_questions, delete_question
from config.settings import ADMIN_IDS

QUESTION_PAGE_SIZE = 5

admin_router = Router()

@admin_router.message(F.text == "/admin")
@admin_router.message(F.text == "🛠 Админ-панель")
async def handle_admin(message: Message, state: FSMContext):
    await message.delete()
    photo = FSInputFile("images/admin_panel.jpg")
    await message.answer_photo(text="Панель администратора:",
                               photo=photo,
                               reply_markup=admin_panel_main_menu)
    await state.set_state(AdminPanelState.active)

@admin_router.message(F.text == "❌ Отмена")
async def handle_add_question(message: Message, state: FSMContext):
    await message.delete()
    photo = FSInputFile("images/admin_panel.jpg")
    await message.answer("🛠 Вы вернулись в админ-панель", reply_markup=admin_main_menu_keyboard())
    await message.answer_photo(text="Панель администратора:",
                               photo=photo,
                               reply_markup=admin_panel_main_menu)
    await state.set_state(AdminPanelState.active)

###################################################################################################

# 📋 Все вопросы
@admin_router.callback_query(F.data == "all_questions")
async def handle_all_questions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    questions = await get_all_questions()
    await state.update_data(question_list=questions)

    try:
        await callback.message.edit_text(
            "📋 Все вопросы:",
            reply_markup=build_question_list_keyboard(questions, page=0, per_page=5)
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            "📋 Все вопросы:",
            reply_markup=build_question_list_keyboard(questions, page=0, per_page=5)
        )

@admin_router.callback_query(F.data.startswith("questions_page_"))
async def handle_question_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    questions = data.get("question_list", [])

    await callback.message.edit_text(
        "📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(questions, page=page, per_page=QUESTION_PAGE_SIZE)
    )

    await state.update_data(current_page=page)

@admin_router.callback_query(F.data.startswith("view_question_"))
async def handle_view_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    question_id = int(callback.data.split("_")[-1])
    data = await state.get_data()

    current_page = data.get("current_page", 0)
    await state.update_data(viewing_from_page=current_page)

    question_id = int(callback.data.split("_")[-1])
    data = await get_all_questions()
    question = next((q for q in data if q.id == question_id), None)
    if not question:
        await callback.answer("Вопрос не найден")
        return

    text = f"📌 <b>Вопрос #{question.id}</b>\n\n"
    text += f"{question.text}\n\n"
    for i, opt in enumerate(question.options):
        mark = "✅" if i == question.correct_index else ""
        text += f"{i+1}. {opt} {mark}\n"
    text += f"\n📊 Сложность: {question.difficulty}"

    await callback.message.edit_text(
        text, reply_markup=view_question_keyboard(question_id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "back_to_question_list")
async def handle_back_to_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    questions = data.get("question_list", [])
    from_page = data.get("viewing_from_page", 0)

    await callback.message.edit_text(
        "📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(questions, page=from_page, per_page=5)
    )

    await state.update_data(current_page=from_page)

###################################################################################################

# ➕ Добавить вопрос
@admin_router.callback_query(F.data == "add_question", AdminPanelState.active)
async def handle_add_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    msg = await callback.message.answer(
        "✍️ Введите текст нового вопроса:", 
        reply_markup=cancel_add_question_reply_keyboard
    )

    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AddQuestionState.text)

@admin_router.message(AddQuestionState.text)
async def process_question_text(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()

    if "msg_id" in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data["msg_id"])
        except:
            pass

    await state.update_data(text=message.text)

    msg = await message.answer(
        "📌 Введите варианты ответа через `;`\n\nПример: Python; Java; C++; Pascal",
        reply_markup=cancel_add_question_reply_keyboard,
        )

    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AddQuestionState.options)

@admin_router.message(AddQuestionState.options)
async def process_question_options(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()

    if "msg_id" in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data["msg_id"])
        except:
            pass

    if "error_msg_id" in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data["error_msg_id"])
        except:
            pass

    options = [opt.strip() for opt in message.text.split(";") if opt.strip()]
    if len(options) < 2:
        err = await message.answer(
            f"❗ Попробуйте ещё раз\n"
            f"❓ Укажите минимум 2 варианта\n\n"
            f"✅ Пример: Python; Java; C++; Pascal"
        )

        await state.update_data(error_msg_id=err.message_id)
        return

    await state.update_data(error_msg_id=None)
    await state.update_data(options=options)

    text = "✅ Варианты приняты:\n" + "\n".join(f"{i+1} - {opt}" for i, opt in enumerate(options))
    text += "\n\nВыберите номер правильного ответа:"

    msg = await message.answer(text, reply_markup=correct_answer_keyboard(options))

    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AddQuestionState.correct_index)

@admin_router.callback_query(F.data.startswith("correct_"), AddQuestionState.correct_index)
async def handle_correct_answer(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("correct_", ""))
    await state.update_data(correct_index=index)

    await callback.message.delete()

    msg = await callback.message.answer(
        "✅ Правильный ответ выбран.\nТеперь выберите уровень сложности:",
        reply_markup=difficulty_choice_keyboard()
    )

    await state.update_data(msg_id=msg.message_id)
    await state.set_state(AddQuestionState.difficulty)

@admin_router.callback_query(F.data.startswith("diff_"), AddQuestionState.difficulty)
async def handle_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.replace("diff_", "")
    if difficulty not in ["easy", "medium", "hard"]:
        await callback.answer("❗ Неверная сложность")
        return

    await state.update_data(difficulty=difficulty)
    data = await state.get_data()

    await callback.message.delete()

    await add_question(
        text=data["text"],
        options=data["options"],
        correct_index=data["correct_index"],
        difficulty=data["difficulty"]
    )

    await callback.message.answer(
        "✅ Вопрос успешно добавлен!",
        reply_markup=admin_main_menu_keyboard()
    )

    await state.clear()

###################################################################################################

# 🗑 Удалить вопрос
@admin_router.callback_query(F.data.startswith("delete_question_"))
async def handle_delete_question(callback: CallbackQuery):
    question_id = int(callback.data.split("_")[-1])

    await callback.message.edit_text(
        f"❗ Вы точно хотите удалить вопрос #{question_id}?",
        reply_markup=confirm_delete_keyboard(question_id)
    )

@admin_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    question_id = int(callback.data.split("_")[-1])
    await delete_question(question_id)

    data = await state.get_data()
    questions = data.get("question_list", [])
    updated_questions = [q for q in questions if q.id != question_id]

    await state.update_data(question_list=updated_questions)

    await callback.message.edit_text(
        "✅ Вопрос удалён!",
        reply_markup=back_to_admin_menu
    )

@admin_router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    questions = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)

    await callback.message.edit_text(
        "📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(
            questions,
            page=current_page,
            per_page=QUESTION_PAGE_SIZE
            )
    )

@admin_router.callback_query(F.data == "back_to_admin_menu")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    questions = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)

    await callback.message.edit_text(
        "📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(
            questions,
            page=current_page,
            per_page=QUESTION_PAGE_SIZE
            )
    )

# ✏️ Редактировать вопрос
@admin_router.callback_query(F.data == "edit_question")
async def handle_edit_question(callback: CallbackQuery):
    await callback.message.edit_text("✏️ Выберите вопрос для редактирования")

# 👤 Назначить админа
@admin_router.callback_query(F.data == "create_admin")
async def handle_create_admin(callback: CallbackQuery):
    await callback.message.edit_text("👤 Введите ID пользователя, которого нужно сделать админом")

@admin_router.callback_query(F.data == "cancel")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()

    await state.clear()

    await callback.message.answer_photo(
        text="🛠 Вы вернулись в админ-панель",
        photo=FSInputFile("images/admin_panel.jpg"),
        reply_markup=admin_panel_main_menu
    )

@admin_router.callback_query(F.data == "back_to_main_menu")
async def hande_back_to_admin_menu(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        "🛠 Вы вернулись в админ-панель",
        reply_markup=admin_main_menu_keyboard()
    )
