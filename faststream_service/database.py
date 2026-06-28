from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
	url = settings.DATABASE_URL_asyncpg,
	echo = True,
)

async_session_factory = async_sessionmaker(async_engine,
											expire_on_commit=False)#expired-устаревшие. False нужен для работы с БД объектами без постоянного запроса к значениям извне