from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.admin_panel.admin_panel_states import AddQuestionState
from keyboards.admin_panel_keyboard import admin_panel_main_menu
from database.requests import add_question

admin_router = Router()

@admin_router.message(F.text == "/admin")
@admin_router.message(F.text == "🛠 Админ-панель")
async def handle_admin(message: Message):
    photo = FSInputFile("images/admin_panel.jpg")
    await message.answer_photo(text="Панель администратора:",
                               photo=photo, 
                               reply_markup=admin_panel_main_menu)

# 📋 Все вопросы
@admin_router.callback_query(F.data == "all_questions")
async def handle_all_questions(callback: CallbackQuery):
    await callback.message.edit_text("📋 Здесь будет список всех вопросов")

# ➕ Добавить вопрос
@admin_router.callback_query(F.data == "add_question")
async def handle_add_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Введите новый вопрос:")
    await state.set_state(AddQuestionState.text)

@admin_router.message(AddQuestionState.text)
async def process_question_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("📌 Введите варианты ответа через `;`\n\nПример: Python; Java; C++; Pascal")
    await state.set_state(AddQuestionState.options)

@admin_router.message(AddQuestionState.options)
async def process_question_options(message: Message, state: FSMContext):
    options = [opt.strip() for opt in message.text.split(";") if opt.strip()]
    if len(options) < 2:
        await message.answer("❗ Укажите минимум 2 варианта.")
        return

    await state.update_data(options=options)
    await message.answer(f"✅ Принято. Вариантов: {len(options)}\n"
                         f"Введите номер правильного ответа (1–{len(options)}):")
    await state.set_state(AddQuestionState.correct_index)

@admin_router.message(AddQuestionState.correct_index)
async def process_correct_index(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        idx = int(message.text) - 1
        if not 0 <= idx < len(data["options"]):
            raise ValueError
    except ValueError:
        await message.answer("❗ Введите корректный номер ответа.")
        return

    await state.update_data(correct_index=idx)
    await message.answer("🧩 Введите уровень сложности: `easy`, `medium`, `hard`")
    await state.set_state(AddQuestionState.difficulty)

@admin_router.message(AddQuestionState.difficulty)
async def process_difficulty(message: Message, state: FSMContext):
    diff = message.text.strip().lower()
    if diff not in ["easy", "medium", "hard"]:
        await message.answer("❗ Введите: `easy`, `medium` или `hard`")
        return

    data = await state.update_data(difficulty=diff)
    data = await state.get_data()

    await add_question(
        text=data["text"],
        options=data["options"],
        correct_index=data["correct_index"],
        difficulty=data["difficulty"]
    )

    await message.answer("✅ Вопрос успешно добавлен!")
    await state.clear()


# 🗑 Удалить вопрос
@admin_router.callback_query(F.data == "delete_question")
async def handle_delete_question(callback: CallbackQuery):
    await callback.message.edit_text("🗑 Выберите вопрос для удаления")

# ✏️ Редактировать вопрос
@admin_router.callback_query(F.data == "edit_question")
async def handle_edit_question(callback: CallbackQuery):
    await callback.message.edit_text("✏️ Выберите вопрос для редактирования")

# 👤 Назначить админа
@admin_router.callback_query(F.data == "create_admin")
async def handle_create_admin(callback: CallbackQuery):
    await callback.message.edit_text("👤 Введите ID пользователя, которого нужно сделать админом")