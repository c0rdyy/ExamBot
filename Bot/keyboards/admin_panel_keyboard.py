from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import ceil

admin_panel_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Все вопросы", callback_data="all_questions"),
    InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_question")],
    [InlineKeyboardButton(text="👤 Назначить админа", callback_data="create_admin")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
    ])

admin_panel_back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
])

back_to_admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin_menu")]
])

cancel_add_question_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=False
)

def correct_answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(i + 1), callback_data=f"correct_{i}")
        for i in range(len(options))
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[buttons, [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]])

def difficulty_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Лёгкий", callback_data="diff_easy")],
            [InlineKeyboardButton(text="Средний", callback_data="diff_medium")],
            [InlineKeyboardButton(text="Сложный", callback_data="diff_hard")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )

def build_question_list_keyboard(questions: list, page: int, per_page: int) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    page_items = questions[start:end]

    buttons = [[
        InlineKeyboardButton(
            text=f"{i+1+start}. {q.text[:25]}", 
            callback_data=f"view_question_{q.id}"
            )
    ] for i, q in enumerate(page_items)]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️ Назад", 
            callback_data=f"questions_page_{page - 1}"
        ))
        buttons.append([
        InlineKeyboardButton(text="⏮ В начало", callback_data="questions_page_0")
    ])
    if end < len(questions):
        nav_buttons.append(InlineKeyboardButton(
            text="▶️ Вперёд", 
            callback_data=f"questions_page_{page + 1}"
        ))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton(text="🔙 В админ-панель", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def view_question_keyboard(question_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️ Редактировать", 
                callback_data=f"edit_question_{question_id}"
            ),
            InlineKeyboardButton(
                text="🗑 Удалить", 
                callback_data=f"delete_question_{question_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад к списку", 
                callback_data="back_to_question_list"
            )
        ]
    ])

def confirm_delete_keyboard(question_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, удалить", 
                callback_data=f"confirm_delete_{question_id}"),
            InlineKeyboardButton(
                text="❌ Отмена", 
                callback_data="cancel_delete")
        ]
    ])