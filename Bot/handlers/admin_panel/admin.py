from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.admin_panel.admin_panel_states import *
from keyboards.admin_panel_keyboard import *
from database.requests import (
    add_question, 
    get_all_questions, 
    delete_question,
    update_question,
    get_question_by_id
    )

QUESTION_PAGE_SIZE = 5

admin_router = Router()

@admin_router.message(F.text == "/admin")
@admin_router.message(F.text == "🛠 Админ-панель")
async def handle_admin(message: Message, state: FSMContext):
    await message.delete()

    photo = FSInputFile("images/admin_panel.jpg")
    msg = await message.answer_photo(
        photo=photo,
        caption="Панель администратора:",
        reply_markup=admin_panel_main_menu
    )
    await state.set_state(AdminPanelState.active)
    await state.update_data(panel_msg_id=msg.message_id)

###################################################################################################

# 📋 Все вопросы
@admin_router.callback_query(F.data == "all_questions")
async def handle_all_questions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    questions = await get_all_questions()
    await state.update_data(question_list=questions)

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    if panel_msg_id:
        try:
            await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=panel_msg_id,
                caption="📋 Все вопросы:",
                reply_markup=build_question_list_keyboard(
                    questions,
                    page=0,
                    per_page=QUESTION_PAGE_SIZE
                    )
            )
        except Exception:
            await callback.message.answer("❗ Не удалось отобразить вопросы")

    await state.set_state(AdminPanelState.viewing_questions)
    await state.update_data(current_page=0)

@admin_router.callback_query(F.data.startswith("questions_page_"))
async def handle_question_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    page = int(callback.data.split("_")[-1])

    data = await state.get_data()
    questions = data.get("question_list", [])
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(
            questions, 
            page=page, 
            per_page=QUESTION_PAGE_SIZE
            )
    )

    await state.update_data(current_page=page)

@admin_router.callback_query(F.data.startswith("view_question_"))
async def handle_view_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    question_id = int(callback.data.split("_")[-1])

    data = await get_all_questions()
    await state.update_data(question_list=data)

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

    fsm_data = await state.get_data()
    panel_msg_id = fsm_data.get("panel_msg_id")
    current_page = fsm_data.get("current_page", 0)
    await state.update_data(viewing_from_page=current_page)

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(question.id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "back_to_question_list")
async def handle_back_to_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    questions = data.get("question_list", [])
    from_page = data.get("viewing_from_page", 0)
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(
            questions, 
            page=from_page, 
            per_page=QUESTION_PAGE_SIZE
            )
    )

    await state.update_data(current_page=from_page)
    await state.set_state(AdminPanelState.viewing_questions)

###################################################################################################

# ➕ Добавить вопрос
@admin_router.callback_query(F.data == "add_question", AdminPanelState.active)
async def handle_add_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    if panel_msg_id:
        await callback.bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=panel_msg_id,
            caption="✍️ Введите текст нового вопроса:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
            ])
        )

    await state.set_state(AddQuestionState.text)

@admin_router.message(AddQuestionState.text)
async def process_question_text(message: Message, state: FSMContext):
    await message.delete()

    data = await state.get_data()
    await state.update_data(text=message.text)

    panel_msg_id = data.get("panel_msg_id")
    caption = (
        "📌 Введите варианты ответа через `;`\n\n"
        "Пример: Python; Java; C++; Pascal"
    )

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=panel_msg_id,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
    )

    await state.set_state(AddQuestionState.options)

@admin_router.message(AddQuestionState.options)
async def process_question_options(message: Message, state: FSMContext):
    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await message.delete()

    options = [opt.strip() for opt in message.text.split(";") if opt.strip()]

    if len(options) < 2:
        error_caption = (
            "❗ Попробуйте ещё раз\n"
            "❓ Укажите минимум 2 варианта через `;`\n\n"
            "✅ Пример: Python; Java; C++; Pascal"
        )

        if panel_msg_id:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=panel_msg_id,
                caption=error_caption,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
                ])
            )
        return

    await state.update_data(options=options)

    text = "✅ Варианты приняты:\n" + "\n".join(f"{i+1} - {opt}" for i, opt in enumerate(options))
    text += "\n\nВыберите номер правильного ответа:"

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=correct_answer_keyboard(options)
    )

    await state.set_state(AddQuestionState.correct_index)

@admin_router.callback_query(F.data.startswith("correct_"), AddQuestionState.correct_index)
async def handle_correct_answer(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("correct_", ""))
    await state.update_data(correct_index=index)

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="✅ Правильный ответ выбран.\nТеперь выберите уровень сложности:",
        reply_markup=difficulty_choice_keyboard()
    )

    await state.set_state(AddQuestionState.difficulty)

@admin_router.callback_query(F.data.startswith("diff_"), AddQuestionState.difficulty)
async def handle_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.replace("diff_", "")
    if difficulty not in ["easy", "medium", "hard"]:
        await callback.answer("❗ Неверная сложность")
        return

    await state.update_data(difficulty=difficulty)
    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await add_question(
        text=data["text"],
        options=data["options"],
        correct_index=data["correct_index"],
        difficulty=difficulty
    )

    await state.clear()
    await state.set_state(AdminPanelState.active)
    await state.update_data(panel_msg_id=panel_msg_id)

    await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=panel_msg_id,
                caption="✅ Вопрос успешно добавлен!\n",
                reply_markup=admin_panel_main_menu
            )


###################################################################################################

# 🗑 Удалить вопрос
@admin_router.callback_query(F.data.startswith("delete_question_"))
async def handle_delete_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    question_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=f"❗ Вы точно хотите удалить вопрос #{question_id}?",
        reply_markup=confirm_delete_keyboard(question_id)
    )

@admin_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    question_id = int(callback.data.split("_")[-1])
    await delete_question(question_id)

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")
    questions = data.get("question_list", [])
    updated_questions = [q for q in questions if q.id != question_id]

    await state.update_data(question_list=updated_questions)

    current_page = data.get("viewing_from_page", 0)
    await state.update_data(current_page=current_page)

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="✅ Вопрос удалён!",
        reply_markup=build_question_list_keyboard(
            updated_questions,
            page=current_page,
            per_page=QUESTION_PAGE_SIZE
        )
    )

@admin_router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    questions = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="📋 Все вопросы:",
        reply_markup=build_question_list_keyboard(
            questions,
            page=current_page,
            per_page=QUESTION_PAGE_SIZE
        )
    )

    await state.update_data(current_page=current_page)


# ✏️ Редактировать вопрос
@admin_router.callback_query(F.data.startswith("edit_question_"))
async def handle_edit_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    question_id = int(callback.data.split("_")[-1])

    data = await get_all_questions()
    question = next((q for q in data if q.id == question_id), None)

    if not question:
        await callback.answer("Вопрос не найден")
        return

    panel_msg_id = (await state.get_data()).get("panel_msg_id")

    text = (
        f"🛠 <b>Редактирование вопроса #{question.id}</b>\n\n"
        f"{question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(question.options))}\n\n"
        f"✅ Ответ: {question.correct_index + 1}\n"
        f"📊 Сложность: {question.difficulty}"
    )

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=edit_question_menu_keyboard(question.id),
        parse_mode="HTML"
    )

    await state.update_data(editing_question_id=question.id)

@admin_router.callback_query(F.data.startswith("edit_text_"))
async def handle_edit_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    question_id = int(callback.data.split("_")[-1])
    await state.set_state(EditQuestionState.editing_text)
    await state.update_data(editing_question_id=question_id)

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=(await state.get_data()).get("panel_msg_id"),
        caption="✏️ Введите новый текст вопроса:",
        reply_markup=cancel_edit_text_field
    )

@admin_router.message(EditQuestionState.editing_text)
async def process_edit_text(message: Message, state: FSMContext):
    await message.delete()
    new_text = message.text

    data = await state.get_data()
    question_id = data.get("editing_question_id")

    if not question_id:
        await message.answer("❗Не удалось получить ID вопроса.")
        return

    await update_question(question_id=question_id, text=new_text)

    updated_question = await get_question_by_id(question_id)
    text = (
        f"📌 <b>Вопрос #{updated_question.id}</b>\n\n"
        f"{updated_question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(updated_question.options))}\n\n"
        f"✅ Ответ: {updated_question.correct_index + 1}\n"
        f"📊 Сложность: {updated_question.difficulty}"
    )


    panel_msg_id = data.get("panel_msg_id")

    await state.set_state(AdminPanelState.active)
    await state.update_data(panel_msg_id=panel_msg_id)

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(updated_question.id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("edit_options_"))
async def handle_edit_options(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    qid = int(callback.data.split("_")[-1])
    await state.set_state(EditQuestionState.editing_options)
    await state.update_data(editing_question_id=qid)

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=(await state.get_data()).get("panel_msg_id"),
        caption="📋 Введите новые варианты через `;`\nПример: Python; Java; C++; C#",
        reply_markup=cancel_edit_options_field
    )

@admin_router.message(EditQuestionState.editing_options)
async def process_edit_options(message: Message, state: FSMContext):
    await message.delete()
    new_options_raw = message.text

    options = [opt.strip() for opt in new_options_raw.split(";") if opt.strip()]
    if len(options) < 2:
        panel_msg_id = (await state.get_data()).get("panel_msg_id")
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=panel_msg_id,
            caption="❗ Нужно минимум 2 варианта. Попробуйте снова.\nПример: Python; Java; C++; C#",
            reply_markup=cancel_edit_options_field
        )
        return

    data = await state.get_data()
    question_id = data.get("editing_question_id")
    panel_msg_id = data.get("panel_msg_id")
    question_list = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)

    await update_question(question_id=question_id, options=options)

    updated_question = await get_question_by_id(question_id)
    text = (
        f"📌 <b>Вопрос #{updated_question.id}</b>\n\n"
        f"{updated_question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(updated_question.options))}\n\n"
        f"✅ Ответ: {updated_question.correct_index + 1}\n"
        f"📊 Сложность: {updated_question.difficulty}"
    )

    await state.set_state(AdminPanelState.viewing_questions)
    await state.update_data(
        panel_msg_id=panel_msg_id,
        question_list=question_list,
        current_page=current_page
    )

    await message.bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(updated_question.id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("edit_answer_"))
async def handle_edit_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    question_id = int(callback.data.split("_")[-1])

    await state.set_state(EditQuestionState.editing_correct_index)
    await state.update_data(editing_question_id=question_id)

    question = await get_question_by_id(question_id)
    panel_msg_id = (await state.get_data()).get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="✅ Выберите номер правильного ответа:",
        reply_markup=editting_correct_answer_keyboard(question.options)
    )

@admin_router.callback_query(F.data.startswith("correct_"), EditQuestionState.editing_correct_index)
async def process_edit_correct_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    correct_index = int(callback.data.replace("correct_", ""))
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    panel_msg_id = data.get("panel_msg_id")
    question_list = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)

    await update_question(question_id=question_id, correct_index=correct_index)

    updated_question = await get_question_by_id(question_id)

    text = (
        f"📌 <b>Вопрос #{updated_question.id}</b>\n\n"
        f"{updated_question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(updated_question.options))}\n\n"
        f"✅ Ответ: {updated_question.correct_index + 1}\n"
        f"📊 Сложность: {updated_question.difficulty}"
    )

    await state.set_state(AdminPanelState.viewing_questions)
    await state.update_data(
        panel_msg_id=panel_msg_id,
        question_list=question_list,
        current_page=current_page
    )

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(updated_question.id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("edit_difficulty_"))
async def handle_edit_difficulty(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    question_id = int(callback.data.split("_")[-1])

    await state.set_state(EditQuestionState.editing_difficulty)
    await state.update_data(editing_question_id=question_id)

    panel_msg_id = (await state.get_data()).get("panel_msg_id")

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption="📊 Выберите уровень сложности:",
        reply_markup=editting_difficulty_choice_keyboard()
    )

@admin_router.callback_query(F.data.startswith("diff_"), EditQuestionState.editing_difficulty)
async def process_edit_difficulty(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    difficulty = callback.data.replace("diff_", "")

    if difficulty not in ["easy", "medium", "hard"]:
        await callback.answer("❗ Неверная сложность")
        return

    data = await state.get_data()
    question_id = data.get("editing_question_id")
    panel_msg_id = data.get("panel_msg_id")
    question_list = data.get("question_list", [])
    current_page = data.get("viewing_from_page", 0)

    await update_question(question_id=question_id, difficulty=difficulty)
    updated_question = await get_question_by_id(question_id)

    text = (
        f"📌 <b>Вопрос #{updated_question.id}</b>\n\n"
        f"{updated_question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(updated_question.options))}\n\n"
        f"✅ Ответ: {updated_question.correct_index + 1}\n"
        f"📊 Сложность: {updated_question.difficulty}"
    )

    await state.set_state(AdminPanelState.viewing_questions)
    await state.update_data(
        panel_msg_id=panel_msg_id,
        question_list=question_list,
        current_page=current_page
    )

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(updated_question.id),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "cancel_edit_field")
async def handle_cancel_edit_field(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    question_id = data.get("editing_question_id")

    if not question_id:
        await callback.answer("❗ Вопрос не найден")
        return

    question = await get_question_by_id(question_id)
    if not question:
        await callback.answer("❗ Вопрос не найден в базе")
        return

    panel_msg_id = data.get("panel_msg_id")
    text = (
        f"🛠 <b>Редактирование вопроса #{question.id}</b>\n\n"
        f"{question.text}\n\n"
        f"{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(question.options))}\n\n"
        f"✅ Ответ: {question.correct_index + 1}\n"
        f"📊 Сложность: {question.difficulty}"
    )

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=edit_question_menu_keyboard(question.id),
        parse_mode="HTML"
    )
    await state.set_state(EditQuestionState.choosing_field)

@admin_router.callback_query(F.data == "back_to_view_question")
async def handle_back_to_view_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    question_id = data.get("editing_question_id")
    panel_msg_id = data.get("panel_msg_id")
    current_page = data.get("viewing_from_page", 0)

    question = await get_question_by_id(question_id)
    if not question:
        await callback.answer("❗Вопрос не найден")
        return

    text = f"📌 <b>Вопрос #{question.id}</b>\n\n"
    text += f"{question.text}\n\n"
    for i, opt in enumerate(question.options):
        mark = "✅" if i == question.correct_index else ""
        text += f"{i+1}. {opt} {mark}\n"
    text += f"\n📊 Сложность: {question.difficulty}"

    await callback.bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=panel_msg_id,
        caption=text,
        reply_markup=view_question_keyboard(question.id),
        parse_mode="HTML"
    )

    await state.update_data(current_page=current_page)
    await state.set_state(AdminPanelState.viewing_questions)


# 👤 Назначить админа
@admin_router.callback_query(F.data == "users_list")
async def handle_create_admin(callback: CallbackQuery):
    await callback.message.edit_text("👤 Введите ID пользователя, которого нужно сделать админом")

@admin_router.callback_query(F.data == "cancel")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=panel_msg_id,
                caption="🛠 Вы вернулись в админ-панель",
                reply_markup=admin_panel_main_menu
            )

    await state.set_state(AdminPanelState.active)
    await state.update_data(panel_msg_id=panel_msg_id)

@admin_router.callback_query(F.data == "back_to_admin_menu")
async def handle_back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    await callback.bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=panel_msg_id,
                caption="🛠 Вы вернулись в админ-панель",
                reply_markup=admin_panel_main_menu
            )

    await state.set_state(AdminPanelState.active)
