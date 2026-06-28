from src.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
	url = settings.DATABASE_URL_asyncpg,
	echo = True,
)

async_session_factoty = async_sessionmaker(async_engine, expire_on_commit=False)

