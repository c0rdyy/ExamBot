from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='👤 Профиль')],
                                     [KeyboardButton(text='📥 Загрузить файл'),
                                      KeyboardButton(text='📂 Запросить файл')],
                                     [KeyboardButton(text='ℹ️ О боте'),
                                      KeyboardButton(text='❓ Помощь')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')