# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
# from sqlalchemy import BigInteger, String

# from config.bot_config import SQLALCHEMY_URL

# engine = create_async_engine(SQLALCHEMY_URL, echo=True)

# async_session = async_sessionmaker(engine)

# class Base(AsyncAttrs, DeclarativeBase):
#     pass

# async def async_main():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


