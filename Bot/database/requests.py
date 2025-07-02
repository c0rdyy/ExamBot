from sqlalchemy import select
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