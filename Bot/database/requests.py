from sqlalchemy import select, delete, update
from sqlalchemy.sql import func

from database.models import async_session, Question, Result, User

async def get_random_questions(difficulty: str, limit: int = 10):
    async with async_session() as session:
        result = await session.execute(
            select(Question).where(Question.difficulty == difficulty).order_by(func.random()).limit(limit)
        )
        return result.scalars().all()

async def save_test_result(user_id: int, score: int, rating_score: float, difficulty: str):
    async with async_session() as session:
        session.add(Result(
            user_id=user_id,
            score=score,
            rating_score=rating_score,
            difficulty=difficulty
        ))
        await session.commit()

async def get_or_create_user(user_id: int, name: str) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()

        return user

async def add_question(text: str, options: list[str], correct_index: int, difficulty: str):
    async with async_session() as session:
        question = Question(
            text=text,
            options=options,
            correct_index=correct_index,
            difficulty=difficulty
        )
        session.add(question)
        await session.commit()

async def get_all_questions():
    async with async_session() as session:
        result = await session.execute(select(Question))
        return result.scalars().all()

async def get_user_profile(user_id: int):
    async with async_session() as session:

        result_user = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result_user.scalar_one_or_none()

        if not user:
            return None

        result_stats = await session.execute(
            select(
                func.count(Result.id),
                func.avg(Result.score),
                func.sum(Result.rating_score)
            ).where(Result.user_id == user_id)
        )
        total_tests, avg_score, total_rating = result_stats.one()

        return {
            "name": user.name,
            "photo_id": user.photo_id,
            "total_tests": total_tests or 0,
            "avg_score": round(avg_score or 0, 2),
            "total_rating": round(total_rating or 0, 2),
        }

async def delete_question(question_id: int):
    async with async_session() as session:
        stmt = delete(Question).where(Question.id == question_id)
        await session.execute(stmt)
        await session.commit()

async def get_question_by_id(question_id: int) -> Question | None:
    async with async_session() as session:
        result = await session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

async def update_question(
    question_id: int,
    text: str | None = None,
    options: list[str] | None = None,
    correct_index: int | None = None,
    difficulty: str | None = None
):
    async with async_session() as session:
        stmt = update(Question).where(Question.id == question_id)

        values = {}
        if text is not None:
            values["text"] = text
        if options is not None:
            values["options"] = options
        if correct_index is not None:
            values["correct_index"] = correct_index
        if difficulty is not None:
            values["difficulty"] = difficulty

        if values:
            stmt = stmt.values(**values)
            await session.execute(stmt)
            await session.commit()

async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.id))
        return result.scalars().all()

async def get_user_by_id(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

async def set_admin_status(user_id: int, is_admin: bool):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_admin = is_admin
            await session.commit()
