from sqlalchemy import select
from sqlalchemy.sql import func
from .models import async_session, Question, Result

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