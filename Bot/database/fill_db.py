import asyncio
from database.models import async_session, Question

async def fill_questions():
    questions = [
        # Easy
        Question(
            text="Что такое класс в ООП?",
            options=["Переменная", "Функция", "Шаблон для объектов", "Условие"],
            correct_index=2,
            difficulty="easy"
        ),
        Question(
            text="Какой модификатор доступа делает поле приватным в Python?",
            options=["public", "_", "__", "private"],
            correct_index=2,
            difficulty="easy"
        ),
        Question(
            text="Что такое объект в ООП?",
            options=["Тип данных", "Экземпляр класса", "Функция", "Код ошибки"],
            correct_index=1,
            difficulty="easy"
        ),

        # Medium
        Question(
            text="Что такое инкапсуляция?",
            options=["Сокрытие данных", "Наследование классов", "Создание функций", "Переопределение методов"],
            correct_index=0,
            difficulty="medium"
        ),
        Question(
            text="Какой метод вызывается при создании объекта?",
            options=["__init__", "__new__", "__call__", "__create__"],
            correct_index=0,
            difficulty="medium"
        ),
        Question(
            text="Какое ключевое слово используется для наследования в Python?",
            options=["inherits", "extends", "class", "нет ключевого слова — просто указывается родительский класс в скобках"],
            correct_index=3,
            difficulty="medium"
        ),

        # Hard
        Question(
            text="Что делает `super()` в методе дочернего класса?",
            options=["Вызывает метод родителя", "Удаляет объект", "Создаёт новый класс", "Ничего не делает"],
            correct_index=0,
            difficulty="hard"
        ),
        Question(
            text="Что такое полиморфизм в ООП?",
            options=["Использование множества языков", "Способность объектов с одинаковым интерфейсом иметь разную реализацию", "Объединение классов", "Множественное наследование"],
            correct_index=1,
            difficulty="hard"
        ),
        Question(
            text="Как реализуется абстрактный класс в Python?",
            options=["Через декоратор @abstractmethod", "Через if", "С помощью try", "Это невозможно"],
            correct_index=0,
            difficulty="hard"
        ),
    ]

    async with async_session() as session:
        session.add_all(questions)
        await session.commit()

    print("✅ Вопросы успешно добавлены в базу данных.")

if __name__ == "__main__":
    asyncio.run(fill_questions())
