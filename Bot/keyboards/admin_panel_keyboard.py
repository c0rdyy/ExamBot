from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from database.models import User

admin_panel_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Все вопросы", callback_data="all_questions"),
    InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_question")],
    [InlineKeyboardButton(text="👤 Список пользователей", callback_data="all_users")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
    ])

admin_panel_back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main_menu")]
])

back_to_admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin_menu")]
])

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
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )

def build_question_list_keyboard(questions: list, page: int, per_page: int) -> InlineKeyboardMarkup:
    start = page * per_page
    end = start + per_page
    page_items = questions[start:end]
    total_pages = (len(questions) - 1) // per_page

    buttons = [[
        InlineKeyboardButton(
            text=f"{start + i + 1}. {q.text[:25]}",
            callback_data=f"view_question_{q.id}"
        )
    ] for i, q in enumerate(page_items)]

    first_last_buttons = []
    if page > 0:
        first_last_buttons.append(InlineKeyboardButton(
            text="⏮ В начало",
            callback_data="questions_page_0"
        ))
    if page < total_pages:
        first_last_buttons.append(InlineKeyboardButton(
            text="⏭ В конец",
            callback_data=f"questions_page_{total_pages}"
        ))
    if first_last_buttons:
        buttons.append(first_last_buttons)

    prev_next_buttons = []

    if page > 0:
        prev_next_buttons.append(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"questions_page_{page - 1}"
        ))
    if end < len(questions):
        prev_next_buttons.append(InlineKeyboardButton(
            text="▶️ Вперёд",
            callback_data=f"questions_page_{page + 1}"
        ))
    if prev_next_buttons:
        buttons.append(prev_next_buttons)

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

def edit_question_menu_keyboard(question_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Текст", callback_data=f"edit_text_{question_id}"),
            InlineKeyboardButton(text="📌 Варианты", callback_data=f"edit_options_{question_id}")
        ],
        [
            InlineKeyboardButton(text="✅ Ответ", callback_data=f"edit_answer_{question_id}"),
            InlineKeyboardButton(text="📊 Сложность", callback_data=f"edit_difficulty_{question_id}")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад к вопросу", callback_data="back_to_view_question")
        ]
    ])

cancel_edit_text_field = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit_field")]
        ])

cancel_edit_options_field = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit_field")]
        ])

def editting_correct_answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(i + 1), callback_data=f"correct_{i}")
        for i in range(len(options))
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons, 
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit_field")
             ]]
    )

def editting_difficulty_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Лёгкий", callback_data="diff_easy")],
            [InlineKeyboardButton(text="Средний", callback_data="diff_medium")],
            [InlineKeyboardButton(text="Сложный", callback_data="diff_hard")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_edit_field")]
        ]
    )

def build_user_list_keyboard(users: List[User], page: int, per_page: int):
    start = page * per_page
    end = start + per_page
    buttons = [
        [InlineKeyboardButton(
            text=f"{u.name or 'Без имени'} (ID: {u.id})", 
            callback_data=f"view_user_{u.id}"
        )]
        for u in users[start:end]
    ]

    nav_buttons = []
    if start > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"users_page_{page - 1}")
        )
    if end < len(users):
        nav_buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=f"users_page_{page + 1}")
        )
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_profile_keyboard(user_id: int, is_admin: bool):
    buttons = []
    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🗑 Убрать права администратора", 
                    callback_data=f"revoke_admin_{user_id}")
            ])
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ Назначить администратором", 
                    callback_data=f"grant_admin_{user_id}")
            ])

    buttons.append(
        [
            InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_user_list")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)